from tascpy.analytics.operations.registry import OperationRegistry

OperationRegistry.discover_domains()
ops = OperationRegistry.get_all_operations()

for name in ["diff", "filter_by_value", "add", "remove_outliers"]:
    if name in ops:
        func = ops[name]
        has_flag = getattr(func, "__tascpy_returns_collection__", False)
        print(f"{name}: __tascpy_returns_collection__ = {has_flag}")
    else:
        print(f"{name} not found")
