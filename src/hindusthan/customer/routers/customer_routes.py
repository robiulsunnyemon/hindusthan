from fastapi import APIRouter, HTTPException,status
from typing import List
from src.hindusthan.customer.models.customer_model import CustomerModel
from src.hindusthan.customer.schemas.customer_schemas import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["customers"])

# GET all customers
@router.get("/", response_model=List[CustomerResponse],status_code=status.HTTP_200_OK)
async def get_all_customers(skip: int = 0, limit: int = 10):
    
    """
    Get all customers with pagination
    """
    customers = await CustomerModel.find_all().skip(skip).limit(limit).to_list()
    return customers

# GET customer by ID
@router.get("/{id}", response_model=CustomerResponse,status_code=status.HTTP_200_OK)
async def get_customer(id: str):
    
    """
    Get customer by ID
    """
    customer = await CustomerModel.get(id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer



# POST create new customer
@router.post("/", response_model=CustomerResponse,status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerCreate):
    
    """
    Create a new customer
    """
    customer_dict = customer_data.model_dump()
    customer = CustomerModel(**customer_dict)
    await customer.create()
    return customer

# PATCH update customer
@router.patch("/{id}", response_model=CustomerResponse,status_code=status.HTTP_200_OK)
async def update_customer(id: str, customer_data: CustomerUpdate):
    
    """
    Update customer information
    """
    customer = await CustomerModel.get(id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    update_data = customer_data.model_dump(exclude_unset=True)
    await customer.update({"$set": update_data})
    return await CustomerModel.get(id)

# DELETE customer
@router.delete("/{id}",status_code=status.HTTP_200_OK)
async def delete_customer(id: str):
    
    """
    Delete customer by ID
    """
    customer = await CustomerModel.get(id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    await customer.delete()
    return {"message": "Customer deleted successfully"}
