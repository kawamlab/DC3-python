from models import Update, ActualMove, Velocity
from dataclasses import asdict, is_dataclass, fields


class Recursion:
    def __init__(self):
        pass

    def tojson(self, obj) -> dict:
        obj_dict:dict = {}
        print(f"obj: {obj}")
        for field in fields(obj):
            value = getattr(obj, field.name)
            if is_dataclass(value):
                obj_dict[field.name] = self.tojson(value)

            else:
                update: str | int | float = value
                obj_dict[field.name] = update
        return obj_dict
                # print(f"{field} is not dataclass")
      # for key, value in obj.items():
      #     if is_dataclass(value):
      #         update = asdict(value)
      #         return self.tojson(update)
      #     else:
      #         update: str | int | float = value
      #         obj[key] = update
      #         return obj


if __name__ == "__main__":
    recursion = Recursion()
    actual_move = ActualMove(rotation="CLOCKWISE", type="TAKEOUT", velocity=Velocity(x=0.0, y=0.0))
    print(recursion.tojson(actual_move))
