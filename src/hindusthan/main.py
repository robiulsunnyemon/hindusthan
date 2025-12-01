from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.hindusthan.database.database import initialize_database, close_database
from fastapi.middleware.cors import CORSMiddleware
from src.hindusthan.auth.routers.user_routes import router as auth_router
from src.hindusthan.customer.routers.customer_routes import router as customer_router
@asynccontextmanager
async def lifespan_context(_: FastAPI):
    await initialize_database()
    yield
    await close_database()



app = FastAPI(
    title="Hindusthan RESTAPI",
    description="Hindusthan is a modern, auth-friendly mobile application designed to bring essential agricultural services directly to farmers through a single digital platform. Developed using Flutter for both Android and iOS, and powered by a secure Python RestAPI + MongoDB backend, the app ensures high performance, reliability, and scalability even in low-connectivity rural environments.",
    version="1.0.0",
    lifespan=lifespan_context,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(auth_router,prefix="/api/v1/users")
app.include_router(customer_router,prefix="/api/v1")


