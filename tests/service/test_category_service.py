import logging
import pytest
from unittest.mock import MagicMock
from werkzeug.exceptions import NotFound

from app.service.dto import CreateCategoryDto
from app.persistent.entity import CategoryEntity, ExpenseCategoryEntity
from app.service.categories import CategoryService

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def mock_category_repo():
    return MagicMock()


@pytest.fixture
def mock_income_repo():
    return MagicMock()


@pytest.fixture
def mock_expense_repo():
    return MagicMock()


@pytest.fixture
def service(mock_category_repo, mock_income_repo, mock_expense_repo):
    return CategoryService(
        category_repository=mock_category_repo,
        income_category_repository=mock_income_repo,
        expense_category_repository=mock_expense_repo
    )


@pytest.fixture
def example_category():
    return CategoryEntity(id=1, name='Salary')


@pytest.fixture
def example_expense_category():
    return ExpenseCategoryEntity(id=1, name='Rent', percentage=30, type_='expense')


def test_add_income_category(service, mock_category_repo, mock_income_repo):
    dto = CreateCategoryDto(name='Salary', category_type='income')
    mock_category_repo.find_by_name.return_value = None
    added_category = service.add_category(dto)

    assert added_category is not None
    assert 'id' in added_category
    assert added_category['name'] == 'Salary'
    assert added_category['category_type'] == 'income'
    mock_category_repo.find_by_name.assert_called_once_with('Salary')
    mock_income_repo.save_or_update.assert_called_once()


def test_add_expense_category(service, mock_category_repo, mock_expense_repo):
    dto = CreateCategoryDto(name='Rent', category_type='expense', percentage=20)
    mock_category_repo.find_by_name.return_value = None
    mock_expense_repo.calculate_all_percentages.return_value = 30
    added_category = service.add_category(dto)

    assert added_category is not None
    assert 'id' in added_category
    assert added_category['name'] == 'Rent'
    assert added_category['category_type'] == 'expense'

    mock_category_repo.find_by_name.assert_called_once_with('Rent')
    mock_expense_repo.calculate_all_percentages.assert_called_once()
    mock_expense_repo.save_or_update.assert_called_once()


def test_add_expense_category_percentage_sum_exceeds_100(service, mock_category_repo, mock_expense_repo):
    dto = CreateCategoryDto(name='Rent', category_type='expense', percentage=30)
    mock_category_repo.find_by_name.return_value = None
    mock_expense_repo.calculate_all_percentages.return_value = 90
    with pytest.raises(ValueError) as err:
        service.add_category(dto)

    assert str(err.value) == 'The sum of percentages cannot exceed 100'


def test_add_category_that_exists(service, mock_category_repo):
    dto = CreateCategoryDto(name='C1', category_type='income')
    mock_category_repo.find_by_name.return_value = MagicMock()

    with pytest.raises(ValueError) as err:
        service.add_category(dto)

    assert str(err.value) == 'Category already exists'


def test_update_expense_percentage(service, mock_category_repo, mock_expense_repo, example_expense_category):
    category = example_expense_category
    mock_expense_repo.find_by_id.return_value = category
    mock_expense_repo.calculate_all_percentages.return_value = 50
    updated_category = service.update_expense_percentage(category_id=1, new_percentage=20)

    assert updated_category is not None
    assert 'id' in updated_category
    assert updated_category['id'] == category.id
    assert updated_category['name'] == category.name
    assert updated_category['percentage'] == 20
    mock_expense_repo.find_by_id.assert_called_once_with(category.id)
    mock_expense_repo.calculate_all_percentages.assert_called_once()


def test_update_expense_percentage_sum_exceeds_100(service, mock_category_repo, mock_expense_repo,
                                                   example_expense_category):
    category = example_expense_category
    mock_expense_repo.find_by_id.return_value = category
    mock_expense_repo.calculate_all_percentages.return_value = 60
    with pytest.raises(ValueError) as err:
        service.update_expense_percentage(category_id=1, new_percentage=80)

    assert str(err.value) == 'The sum of percentages cannot exceessd 100'


def test_update_expense_percentage_category_not_found(service, mock_category_repo, mock_expense_repo):
    mock_expense_repo.find_by_id.return_value = None
    with pytest.raises(NotFound) as err:
        service.update_expense_percentage(category_id=1, new_percentage=20)

    assert str(err.value) == '404 Not Found: Category not found'


def test_get_category_by_name(service, mock_category_repo):
    category = CategoryEntity(id=1, name='Salary')
    mock_category_repo.find_by_name.return_value = category
    found_category = service.get_by_name(name='Salary')

    assert found_category is not None
    assert found_category['id'] == 1
    assert found_category['name'] == 'Salary'


def test_get_category_by_name_not_found(service, mock_category_repo):
    category = CategoryEntity(id=1, name='Salary')
    mock_category_repo.find_by_name.return_value = None
    with pytest.raises(NotFound) as err:
        found_category = service.get_by_name(name='Salary')
        assert found_category is not category
        assert found_category is None

    assert str(err.value) == '404 Not Found: Category not found'


def test_delete_category_by_name(service, mock_category_repo, example_category):
    service.delete_by_name(name=example_category.name)
    mock_category_repo.delete_by_name.assert_called_once_with(example_category.name)


def test_calculate_percentages_sum(service, mock_expense_repo):
    mock_expense_repo.calculate_all_percentages.return_value = 55
    all_percentages = service.calculate_percentages_sum(new_percentage=30)
    assert all_percentages == 85
    mock_expense_repo.calculate_all_percentages.assert_called_once()
