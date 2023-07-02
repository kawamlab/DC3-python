import json
from dataclasses import fields, is_dataclass

from models import ActualMove, Update, Velocity


class Recursion:
    def __init__(self):
        self.obj_dict = {}
        pass

    def to_json(self, obj, check):
        f = open("learning_data12.json", "a", encoding="UTF-8")
        print(obj)

        for field in fields(obj):
            value = getattr(obj, field.name)
            # if value is None:
            #     obj_dict[field.name] = None

            if is_dataclass(value):
                self.obj_dict[field.name] = self.to_json(value, False)
            elif isinstance(value, list):
                self.obj_dict[field.name] = [self.to_json(v, False) for v in value]
            elif isinstance(value, dict):
                self.obj_dict[field.name] = {k: self.to_json(v, False) for k, v in value.items()}
            elif isinstance(value, tuple):
                self.obj_dict[field.name] = tuple(self.to_json(v, False) for v in value)
            else:
                update: str | int | float = value
                self.obj_dict[field.name] = update

        if check is True:
            json.dump(self.obj_dict, f)
            print(self.obj_dict)
            f.close()
        # return self.obj_dict

        # print(f"{field} is not dataclass")

    # for key, value in obj.items():
    #     if is_dataclass(value):
    #         update = asdict(value)
    #         return self.to_json(update)
    #     else:
    #         update: str | int | float = value
    #         obj[key] = update
    #         return obj


# if __name__ == "__main__":
#     recursion = Recursion()
#     actual_move = ActualMove(rotation="CLOCKWISE", type="TAKEOUT", velocity=Velocity(x=0.0, y=0.0))
#     recursion.to_json(actual_move)
# f=open("learning_data11.json", "w", encoding="UTF-8")
# f.writelines(recursion.to_json(actual_move))
# f.close()
# print(recursion.to_json(actual_move))
