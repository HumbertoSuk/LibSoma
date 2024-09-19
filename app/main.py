"""Aplicación principal"""

from fastapi import FastAPI
from app.routers import auth, users, roles, categories, books, loans, loans_histories, books_reservations, fines

app = FastAPI()

# Rutas de los endpoints
app.include_router(auth.router,  tags=["Authentication"])
app.include_router(users.router,  tags=["Users"])
app.include_router(roles.router, tags=["Roles"])
app.include_router(categories.router,
                   tags=["Categories"])
app.include_router(books.router, tags=["Books"])
app.include_router(loans.router,  tags=["Loans"])
app.include_router(loans_histories.router,
                   tags=["Loan Histories"])
app.include_router(books_reservations.router,
                   tags=["Book Reservations"])
app.include_router(fines.router, tags=["Fines"])
