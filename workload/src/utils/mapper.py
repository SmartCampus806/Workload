def map_dto_to_model(dto, model):
    for i in dto.__dict__:
        model.__setattr__(i, dto.__dict__[i])
    return model