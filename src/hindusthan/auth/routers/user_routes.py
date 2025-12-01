from datetime import datetime,timedelta,timezone
from fastapi import APIRouter, HTTPException,status,Depends
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from src.hindusthan.auth.models.user_model import UserModel, OTPModel, UserRole
from src.hindusthan.auth.schemas.user_schemas import UserCreate, UserUpdate, UserResponse, OTPVerify, Token, ResendOTP, \
    GoogleLoginRequest
from src.hindusthan.auth.utils.auth_utils import hash_password, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, GOOGLE_CLIENT_ID
import random
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token



router = APIRouter( tags=["users"])





# GET all users
@router.get("/", response_model=List[UserResponse],status_code=status.HTTP_200_OK)
async def get_all_users(skip: int = 0, limit: int = 10):
    
    """
    Get all users with pagination
    """
    users = await UserModel.find_all().skip(skip).limit(limit).to_list()
    return users

# GET auth by ID
@router.get("/{id}", response_model=UserResponse,status_code=status.HTTP_200_OK)
async def get_user(id: str):
    
    """
    Get auth by ID
    """
    user = await UserModel.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user



# POST create new user
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Create a new user with OTP verification
    """

    # Check if user already exists
    existing_user = await UserModel.find_one(UserModel.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    def generate_otp():
        return str(random.randint(100000, 999999))

    # Generate OTP - FIXED: Use timezone aware datetime
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # Hash password
    hash_pass = hash_password(user_data.password)

    # Delete existing OTPs for this email
    await OTPModel.find(OTPModel.email == user_data.email).delete()

    # Create and save OTP
    otp = OTPModel(
        email=user_data.email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    await otp.insert()

    # Create user
    user_dict = user_data.model_dump()
    user_dict["password"] = hash_pass
    user = UserModel(**user_dict)
    await user.insert()

    return {
        "message": "User created successfully. Please verify your email with OTP.",
        "user_id": str(user.id),
        "email": user.email,
        "is_verified": user.is_verified,
        "otp": otp_code  # Remove this in production
    }


## POST verify otp
@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(request: OTPVerify):
    """
    Verify OTP for user registration
    """
    if not request.email or not request.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and OTP code are required"
        )

    # Find the OTP record
    otp_record = await OTPModel.find_one(
        OTPModel.email == request.email,
        OTPModel.otp_code == request.otp_code
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )

    # FIXED: Make both datetime objects timezone aware for comparison
    current_time = datetime.now(timezone.utc)

    # If expires_at is naive, make it aware
    if otp_record.expires_at.tzinfo is None:
        expires_at_aware = otp_record.expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at_aware = otp_record.expires_at

    # Check if OTP has expired
    if current_time > expires_at_aware:
        await otp_record.delete()  # Delete expired OTP
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired"
        )

    # Find the user
    user = await UserModel.find_one(UserModel.email == request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if user is already verified
    if user.is_verified:
        await otp_record.delete()  # Clean up OTP
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already verified"
        )

    # Mark user as verified
    user.is_verified = True
    await user.save()

    # Delete the used OTP
    await otp_record.delete()

    return {
        "message": "OTP verified successfully",
        "user_id": str(user.id),
        "email": user.email,
        "is_verified": True,
        "verified_at": datetime.now(timezone.utc)
    }




@router.post("/resend-otp",status_code=status.HTTP_200_OK)
async def resend_otp(request:ResendOTP):
    """
    Resend OTP for email verification
    """

    email=request.email

    # Check if user exists and not verified
    user = await UserModel.find_one(UserModel.email==email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    def generate_otp():
        return str(random.randint(100000, 999999))

    # Generate OTP - FIXED: Use timezone aware datetime
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)


    # Delete existing OTPs for this email
    await OTPModel.find(OTPModel.email == email).delete()

    # Create and save OTP
    otp = OTPModel(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    await otp.insert()



    return {"message": "OTP sent successfully","otp":otp_code}


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    user =await UserModel.find_one(UserModel.email==form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your Email or password is wrong",
            headers={"WWW-Authenticate": "Bearer"},
        )


    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email,"id":user.id},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}




# PATCH update auth
@router.patch("/{id}", response_model=UserResponse,status_code=status.HTTP_200_OK)
async def update_user(id: str, user_data: UserUpdate):
    
    """
    Update auth information
    """
    user = await UserModel.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    await user.update({"$set": update_data})
    return await UserModel.get(id)

# DELETE auth
@router.delete("/{id}",status_code=status.HTTP_200_OK)
async def delete_user(id: str):
    
    """
    Delete auth by ID
    """
    user = await UserModel.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await user.delete()
    return {"message": "User deleted successfully"}





@router.post("/login-with-google", response_model=Token, status_code=status.HTTP_200_OK)
async def login_with_google(request: GoogleLoginRequest):
    """
    Authenticate user using Google ID Token and issue a JWT.
    """
    try:
        if not request.id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID Token is required"
            )

        # Validate the ID token using Google's official library
        id_info = id_token.verify_oauth2_token(
            request.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID  # Your Google OAuth client ID
        )

        # Validate the token audience
        if id_info['aud'] not in [GOOGLE_CLIENT_ID]:
            raise ValueError("Invalid token audience")

        email = id_info["email"]
        name = id_info.get("name", "")
        picture = id_info.get("picture", "")
        google_id = id_info["sub"]  # Use Google's unique user ID, not email

        # Verify email is present and verified by Google
        if not email or not id_info.get("email_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified by Google"
            )

    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Find or create user
    user = await UserModel.find_one(UserModel.email == email)

    if user:
        # Update user information if needed
        update_fields = {}
        if not user.is_verified:
            update_fields["is_verified"] = True
        if not user.google_id:
            update_fields["google_id"] = google_id
        if picture and user.image_url != picture:
            update_fields["image_url"] = picture

        if update_fields:
            await user.update({"$set": update_fields})

    else:
        # Create new user
        new_user = UserModel(
            email=email,
            google_id=google_id,  # Use Google's user ID, not email
            image_url=picture,
            is_verified=True,
            role=UserRole.CUSTOMER
        )
        await new_user.insert()
        user = new_user

    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "id": str(user.id),  # Ensure ID is string
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }