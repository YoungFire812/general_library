from fastapi import HTTPException, status

class ResponseHandler:
    @staticmethod
    async def success(message, data=None):
        return {"message": message, "data": data}

    @staticmethod
    async def get_single_success(name, id, data):
        message = f"Details for {name} with id {id}"
        return await ResponseHandler.success(message, data)

    @staticmethod
    async def create_success(name, id, data):
        message = f"{name} with id {id} created successfully"
        return await ResponseHandler.success(message, data)

    @staticmethod
    async def update_success(name, id, data):
        message = f"{name} with id {id} updated successfully"
        return await ResponseHandler.success(message, data)

    @staticmethod
    async def delete_success(name, id, data):
        message = f"{name} with id {id} deleted successfully"
        return await ResponseHandler.success(message, data)

    @staticmethod
    async def not_found_error(name="", id=None):
        message = f"{name} With Id {id} Not Found!"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    @staticmethod
    async def invalid_token(name=""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid {name} token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
