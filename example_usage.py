#!/usr/bin/env python3
"""
Example usage of the XDM Views Query Engine

This script demonstrates:
1. Loading metadata and views
2. Executing different federated queries
3. Processing and displaying results
"""

import os
import json
from query_engine import MetaSchemaLoader, ViewLoader, QueryExecutor

def print_results(view_name: str, results: list):
    """Pretty print query results"""
    print(f"\n{'=' * 80}")
    print(f"VIEW: {view_name}")
    print(f"{'=' * 80}")
    
    if not results:
        print("No results")
        return
    
    # Get all unique keys from all rows
    all_keys = set()
    for row in results:
        all_keys.update(row.keys())
    
    # Print header
    keys = sorted(all_keys)
    header = " | ".join(f"{k:15}" for k in keys)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in results:
        values = [str(row.get(k, '')).rjust(15) for k in keys]
        print(" | ".join(values))
    
    print(f"\nTotal rows: {len(results)}")


def main():
    """Main example execution"""
    
    # Set up paths
    base_path = '/Users/paragkatoch/Downloads/downloads/term 2/subs/DM/proj/phase1'
    
    print("\n" + "=" * 80)
    print("XDM Views - Federated Query Engine Example")
    print("=" * 80)
    
    # Step 1: Load metadata
    print("\n[Step 1] Loading Metadata...")
    metaschema = MetaSchemaLoader(os.path.join(base_path, 'MetaSchema.xml'))
    views = ViewLoader(os.path.join(base_path, 'views/views.xml'))
    print(f"  ✓ Loaded {len(metaschema.entities)} entities")
    print(f"  ✓ Loaded {len(metaschema.databases)} databases")
    print(f"  ✓ Loaded {len(views.views)} views")
    
    # Step 2: Create query executor
    print("\n[Step 2] Initializing Query Executor...")
    executor = QueryExecutor(
        metaschema,
        views,
        os.path.join(base_path, 'dummy_data/customers.db'),
        os.path.join(base_path, 'dummy_data/purchaseorders.xml')
    )
    print("  ✓ Connected to databases")
    
    # Step 3: Display available views
    print("\n[Step 3] Available Views:")
    for view_name in views.views.keys():
        view = views.views[view_name]
        print(f"  • {view_name}")
        print(f"    - Entities: {', '.join(view['base_entities'])}")
        if view['filter']:
            f = view['filter']
            print(f"    - Filter: {f.entity}.{f.attribute} {f.operator} '{f.value}'")
    
    # Step 4: Execute views
    print("\n[Step 4] Executing Views...")
    
    # Execute HighValueCustomers
    print("\n  Executing HighValueCustomers...")
    print("  (Customers with purchase amount > 10,000)")
    results_hvl = executor.execute_view('HighValueCustomers')
    print(f"  ✓ Got {len(results_hvl)} result rows")
    
    # Execute CustomersByItem
    print("\n  Executing CustomersByItem...")
    print("  (Customers who purchased Laptop items)")
    results_item = executor.execute_view('CustomersByItem')
    print(f"  ✓ Got {len(results_item)} result rows")
    
    # Execute CustomerPurchases
    print("\n  Executing CustomerPurchases...")
    print("  (All purchases for customer_id = 5)")
    results_cust = executor.execute_view('CustomerPurchases')
    print(f"  ✓ Got {len(results_cust)} result rows")
    
    # Step 5: Display results
    print("\n[Step 5] Query Results")
    print_results('HighValueCustomers', results_hvl)
    print_results('CustomersByItem', results_item)
    print_results('CustomerPurchases', results_cust)
    
    # Step 6: Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    # Analyze HighValueCustomers
    print("\nHighValueCustomers Analysis:")
    unique_customers = set(row['customer_id'] for row in results_hvl)
    print(f"  - Unique customers: {len(unique_customers)}")
    print(f"  - Total purchase orders: {len(results_hvl)}")
    total_amount = sum(int(row['amount']) for row in results_hvl)
    print(f"  - Total purchase amount: {total_amount:,}")
    
    # Analyze CustomersByItem
    print("\nCustomersByItem Analysis:")
    print(f"  - Customers who bought Laptops: {len(set(row['customer_id'] for row in results_item))}")
    print(f"  - Total Laptop orders: {len(results_item)}")
    
    # Analyze CustomerPurchases
    print("\nCustomerPurchases Analysis:")
    if results_cust:
        customer_ids = set(row.get('customer_id') for row in results_cust)
        customer_id = list(customer_ids)[0] if customer_ids else 'Unknown'
        total_spent = sum(int(row['amount']) for row in results_cust)
        print(f"  - Customer ID: {customer_id}")
        print(f"  - Number of purchases: {len(results_cust)}")
        print(f"  - Total spent: {total_spent:,}")
    
    # Step 7: Cleanup
    print("\n[Step 6] Cleanup...")
    executor.close()
    print("  ✓ Database connections closed")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
