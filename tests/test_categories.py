from datetime import datetime, timezone
from src.services.categories import CategoryService
from src.schemas.categories import CategoryCreate, CategoryUpdate
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class TestGetAllCategories:
    async def test_get_all_only_active(self, db_session, test_category, another_category):
        another_category.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        result = await CategoryService.get_all_categories(db_session)

        assert len(result) == 1
        assert result[0].id == test_category.id

    async def test_empty(self, db_session):
        result = await CategoryService.get_all_categories(db_session)
        assert result == []


class TestGetAllCategoriesIncludingDeleted:
    async def test_get_all_with_deleted(self, db_session, test_category, another_category):
        another_category.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        result = await CategoryService.get_all_categories_including_deleted(db_session)

        assert len(result) == 2


class TestGetOneCategory:
    async def test_success(self, db_session, test_category):
        result = await CategoryService.get_one_category(db_session, test_category.id)
        assert result.id == test_category.id

    async def test_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc:
            await CategoryService.get_one_category(db_session, 999)

        assert exc.value.status_code == 404

    async def test_deleted_category(self, db_session, test_category):
        test_category.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        with pytest.raises(HTTPException) as exc:
            await CategoryService.get_one_category(db_session, test_category.id)

        assert exc.value.status_code == 404


class TestCreateCategory:
    async def test_success(self, db_session):
        data = CategoryCreate(name="New Category")

        result = await CategoryService.create_category(db_session, data)

        assert result.id is not None
        assert result.name == "New Category"

    async def test_duplicate_name(self, db_session, test_category):
        data = CategoryCreate(name=test_category.name)

        with pytest.raises(IntegrityError):
            await CategoryService.create_category(db_session, data)


class TestUpdateCategory:
    async def test_success(self, db_session, test_category):
        data = CategoryUpdate(name="Updated")

        result = await CategoryService.update_category(
            db_session,
            test_category.id,
            data
        )

        assert result.name == "Updated"

    async def test_not_found(self, db_session):
        data = CategoryUpdate(name="Updated")

        with pytest.raises(HTTPException) as exc:
            await CategoryService.update_category(db_session, 999, data)

        assert exc.value.status_code == 404

    async def test_no_fields(self, db_session, test_category):
        data = CategoryUpdate()

        with pytest.raises(HTTPException) as exc:
            await CategoryService.update_category(
                db_session,
                test_category.id,
                data
            )

        assert exc.value.status_code == 400

    async def test_ignore_none(self, db_session, test_category):
        data = CategoryUpdate(name=None)

        with pytest.raises(HTTPException):
            await CategoryService.update_category(
                db_session,
                test_category.id,
                data
            )

    async def test_deleted_category(self, db_session, test_category):
        test_category.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        data = CategoryUpdate(name="Updated")

        with pytest.raises(HTTPException) as exc:
            await CategoryService.update_category(
                db_session,
                test_category.id,
                data
            )

        assert exc.value.status_code == 404


class TestDeleteCategory:
    async def test_success(self, db_session, test_category):
        await CategoryService.delete_category(db_session, test_category.id)

        assert test_category.deleted_at is not None

    async def test_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc:
            await CategoryService.delete_category(db_session, 999)

        assert exc.value.status_code == 404

    async def test_already_deleted(self, db_session, test_category):
        test_category.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        with pytest.raises(HTTPException):
            await CategoryService.delete_category(db_session, test_category.id)
