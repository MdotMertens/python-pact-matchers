def handler(event: dict, context: dict) -> int:
    if event.get("delivery_type") != "standard":
        raise Exception("Not supported")
    print(event.get("customer"))
    if not isinstance(event.get("customer"), str):
        raise Exception("Delivery requires a customer")
    return 1
