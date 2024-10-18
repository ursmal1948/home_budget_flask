from app.persistent.entity import UserEntity


class TestUserModel:
    def test_when_user_is_created_correctly(self, user_data):
        user = UserEntity(**user_data)

        assert ((user_data['name'], user_data['email'], user_data['roles'], user_data['is_active'])
                == (user.name, user.email, user.roles, user.is_active))

    def test_user_to_dict(self, user_data):
        user = UserEntity(**user_data)
        user_to_dict = user.to_dict()
        assert (user_to_dict['name'], user_to_dict['email'], user_to_dict['roles'], user_to_dict['is_active']) == (
            user.name, user.email, user.roles, user.is_active
        )
