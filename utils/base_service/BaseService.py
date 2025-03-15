class BaseService:
    def __init__(self, service_name, svc_indx, total_svcs=3):
        self.service_name = service_name
        self.svc_indx = svc_indx
        self.total_svcs = total_svcs
        self.orders = {}
        print(f"{self.service_name} initialized. Service index: {self.svc_indx}.")

    # Saves information about the order and creates a vector clock for the actions on the order
    def init_order(self, order_id, data):
        self.orders[order_id] = {"data": data, "vc": [0]*self.total_svcs}

    # Combines local and incoming vector clocks by taking biggest value for each service, and adds 1 to current service
    def merge_and_increment(self, local_vc, incoming_vc):
        for i in range(self.total_svcs):
            local_vc[i] = max(local_vc[i], incoming_vc[i])
        local_vc[self.svc_indx] += 1

    def verify_items(self, order_id, incoming_vc):
        entry = self.orders[order_id]["data"]
        self.merge_and_increment(entry, incoming_vc)
        # dummy check
        if not entry["data"].items:
            return {"fail": True, "vc": entry["vc"]}
        return {"fail": False, "vc": entry["vc"]}