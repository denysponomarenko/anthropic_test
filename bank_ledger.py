class BankLedger:

    def __init__(self):
        self.accounts = {}      # id -> balance
        self.outgoing = {}      # id -> total outgoing
        self.history = {}       # id -> [(timestamp, balance)]
        self.payments = {}      # payment_id -> payment info
        self.payment_count = 0

    def _cashback(self, timestamp):
        for payment_id, p in self.payments.items():
            if p["status"] == "IN_PROGRESS" and p["due"] <= timestamp:
                self.accounts[p["account"]] += p["cashback"]
                p["status"] = "CASHBACK_RECEIVED"

                self.history[p["account"]].append(
                    (p["due"], self.accounts[p["account"]])
                )

    def create_account(self, timestamp, account_id):
        self._cashback(timestamp)

        if account_id in self.accounts:
            return "false"

        self.accounts[account_id] = 0
        self.outgoing[account_id] = 0
        self.history[account_id] = [(timestamp, 0)]

        return "true"

    def deposit(self, timestamp, account_id, amount):
        self._cashback(timestamp)

        if account_id not in self.accounts:
            return ""

        self.accounts[account_id] += amount

        self.history[account_id].append(
            (timestamp, self.accounts[account_id])
        )

        return str(self.accounts[account_id])

    def transfer(self, timestamp, source, target, amount):
        self._cashback(timestamp)

        if source not in self.accounts or target not in self.accounts:
            return ""

        if source == target:
            return ""

        if self.accounts[source] < amount:
            return ""

        self.accounts[source] -= amount
        self.accounts[target] += amount

        self.outgoing[source] += amount

        self.history[source].append(
            (timestamp, self.accounts[source])
        )
        self.history[target].append(
            (timestamp, self.accounts[target])
        )

        return str(self.accounts[source])

    def top_spenders(self, timestamp, n):
        self._cashback(timestamp)

        if not self.accounts:
            return ""

        ids = sorted(
            self.accounts,
            key=lambda x: (-self.outgoing[x], x)
        )

        return ", ".join(
            f"{x}({self.outgoing[x]})"
            for x in ids[:n]
        )

    def pay(self, timestamp, account_id, amount):
        self._cashback(timestamp)

        if account_id not in self.accounts:
            return ""

        if self.accounts[account_id] < amount:
            return ""

        self.accounts[account_id] -= amount
        self.outgoing[account_id] += amount

        self.payment_count += 1
        payment_id = f"payment{self.payment_count}"

        self.payments[payment_id] = {
            "account": account_id,
            "cashback": amount * 2 // 100,
            "due": timestamp + 24 * 60 * 60 * 1000,
            "status": "IN_PROGRESS"
        }

        self.history[account_id].append(
            (timestamp, self.accounts[account_id])
        )

        return payment_id

    def get_payment_status(self, timestamp, account_id, payment_id):
        self._cashback(timestamp)

        if payment_id not in self.payments:
            return ""

        payment = self.payments[payment_id]

        if payment["account"] != account_id:
            return ""

        return payment["status"]

    def get_balance(self, timestamp, account_id, past_timestamp):
        self._cashback(timestamp)

        if account_id not in self.accounts:
            return ""

        result = ""

        for t, balance in self.history[account_id]:
            if t <= past_timestamp:
                result = str(balance)
            else:
                break

        return result
