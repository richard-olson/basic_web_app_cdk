
def create_user_data(substitution_dictionary, dns):
    with open("./user_data/user_data.sh") as initial_user_data:
        user_data = initial_user_data.read()
        for line in user_data:
            for k, v in substitution_dictionary.items():
                user_data = user_data.replace(k, str(v))
            user_data = user_data.replace('alb_dns', dns)

    return user_data
