import networkx as nx
import matplotlib.pyplot as plt
import random
import datetime

def draw_graph(G, fraud_transactions):
    pos = nx.spring_layout(G)

    plt.figure(figsize=(12, 8))
    ax = plt.gca()

    # Collect edges to determine the number of parallel edges
    edge_dict = {}
    for source, target, data in G.edges(data=True):
        if (source, target) not in edge_dict:
            edge_dict[(source, target)] = []
        edge_dict[(source, target)].append(data)

    # Determine node colors
    node_colors = []
    fraud_nodes = set()
    for transaction in fraud_transactions:
        fraud_nodes.add(transaction[0])
        fraud_nodes.add(transaction[1])

    for node in G.nodes():
        if node in fraud_nodes:
            node_colors.append('red')
        else:
            node_colors.append('skyblue')

    # Draw edges with different colors for fraudulent transactions
    for (source, target), datas in edge_dict.items():
        for i, data in enumerate(datas):
            amount = data['amount']
            color = 'red' if (source, target, amount) in [(x[0], x[1], x[2]) for x in fraud_transactions] else '0.5'
            rad = 0.1 * (i - (len(datas) - 1) / 2)  # Adjust curvature for each parallel edge
            ax.annotate("",
                        xy=pos[target], xycoords='data',
                        xytext=pos[source], textcoords='data',
                        arrowprops=dict(arrowstyle="->",
                                        color=color,
                                        shrinkA=5,
                                        shrinkB=5,
                                        connectionstyle=f"arc3,rad={rad}",
                                        lw=2))

    nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold', ax=ax)

    edge_labels = {(source, target): f'{data["amount"]}' for source, target, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12, ax=ax)

    plt.tight_layout()
    plt.savefig("C:\\Users\\LENOVO\\Downloads\\GT_MINIPROJECT\\static\\graph.png")
    plt.close()


def detect_fraud(transaction_data):
    # Create a directed multigraph from transaction data
    G = nx.MultiDiGraph()
    for transaction in transaction_data:
        source_account, target_account, amount, timestamp, account_age, balance = transaction
        G.add_edge(source_account, target_account, amount=amount, timestamp=timestamp, account_age=account_age, balance=balance)

    # Calculate node features
    node_degrees = dict(G.degree())
    node_betweenness = nx.betweenness_centrality(G)

    # Identify potential fraud based on anomalies in node features and transaction amounts
    fraud_transactions = []
    fraud_reason = []  # Store reasons for fraud

    for transaction in transaction_data:
        source_account, target_account, amount, timestamp, account_age, balance = transaction
        source_degree = node_degrees.get(source_account, 0)
        source_betweenness = node_betweenness.get(source_account, 0)
        transaction_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        transaction_hour = transaction_time.hour

        fraud_reasons = []  # Reset fraud reasons for each transaction

        # Fraud detection rules
        if amount > 10000:  # High transaction amount
            fraud_reasons.append("High transaction amount")
        if source_degree > 3:  # High node degree
            fraud_reasons.append("High node degree")
        if source_betweenness > 0.1:  # High betweenness centrality
            fraud_reasons.append("High betweenness centrality")
        if transaction_hour < 6 or transaction_hour > 22:  # Unusual transaction time
            fraud_reasons.append("Unusual transaction time")
        if account_age < 30:  # Account age less than 30 days
            fraud_reasons.append("Account age less than 30 days")
        if balance and amount > 0.8 * balance:  # High amount relative to account balance
            fraud_reasons.append("High amount relative to account balance")

        # Append the transaction to fraud_transactions if any fraud reason is found
        if fraud_reasons:
            fraud_transactions.append(transaction)
            fraud_reason.append(", ".join(fraud_reasons))  # Store reasons for fraud as a string

    # Draw the graph
    draw_graph(G, fraud_transactions)

    return fraud_transactions, fraud_reason


def generate_random_transactions(num_transactions):
    accounts = [chr(i) for i in range(65, 65 + num_transactions)]
    transactions = []
    for _ in range(num_transactions):
        source = random.choice(accounts)
        target = random.choice(accounts)
        while target == source:
            target = random.choice(accounts)
        amount = random.randint(50, 2000)
        timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 100))).strftime('%Y-%m-%d %H:%M:%S')
        account_age = random.randint(0, 100)  # Account age in days
        balance = random.randint(500, 5000)  # Account balance
        transactions.append((source, target, amount, timestamp, account_age, balance))
    return transactions
