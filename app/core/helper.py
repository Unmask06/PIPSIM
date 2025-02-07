import inspect
from typing import Dict, List


def get_string_values_from_class(class_names: type | list[type]) -> list:
    def extract_string_values(class_name):
        return sorted(
            [
                value
                for key, value in class_name.__dict__.items()
                if not key.startswith("__") and isinstance(value, str)
            ]
        )

    combined_values = set()

    def get_inherited_classes(class_name):
        for _class in inspect.getmro(class_name):
            if _class.__name__ == "object":
                break
            combined_values.update(extract_string_values(_class))
        return combined_values

    if isinstance(class_names, list):
        for class_name in class_names:
            get_inherited_classes(class_name)
    else:
        get_inherited_classes(class_names)

    return sorted(combined_values)


def get_class_by_name(abstract_class: type, class_name: str) -> type:
    """
    Dynamically retrieves a class from the Parameters module by its name.
    """
    try:
        # Dynamically get the class from Parameters
        class_object = getattr(abstract_class, class_name)
        return class_object
    except AttributeError:
        raise ValueError(f"Class '{class_name}' not found in Parameters.")


def generate_dict_from_class(class_name: type) -> Dict[str, List[str]]:
    """
    Generates a dictionary from a class with string attributes.
    """

    def is_valid_component(component):
        return not component.startswith("__")

    components = sorted(filter(is_valid_component, class_name.__dict__.keys()))
    return {
        component: get_string_values_from_class(
            get_class_by_name(class_name, component)
        )
        for component in components
    }
