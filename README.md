# XDM Views - Cross Data Model Query Engine

A federated query engine that enables querying across multiple heterogeneous databases (Relational and XML) using a unified logical view interface.

## Project Overview

This project implements a federated database system that allows a single logical query to:

- Retrieve data from multiple databases (SQL and XML)
- Use XPath expressions for XML queries
- Use SQL for relational queries
- Join and merge results back into a tabular format

## Architecture

### Three-Layer Metadata Architecture

1. **Meta-Meta Schema** (`metaMetaSchema.xml`) - XSD schema

   - Defines the structure of the metadata system itself
   - Validates MetaSchema.xml

2. **Meta Schema** (`MetaSchema.xml`) - Global schema layer

   - Describes all databases and their entities
   - Defines attributes and relationships
   - Maps logical names to physical paths (e.g., XPath for XML)

3. **Views** (`views/views.xml`) - Logical view definitions
   - Define what "logical queries" look like
   - Specify projections, filters, and joins
   - Database-agnostic specifications

### Components

- **query_engine.py** - Main execution engine
  - `MetaSchemaLoader`: Parses the metadata schema
  - `ViewLoader`: Parses view definitions
  - `QueryExecutor`: Coordinates query execution across databases
- **dummy_data/** - Sample data
  - `customers.db`: SQLite database with relational data
  - `purchaseorders.xml`: XML data file
  - `create_database.sql`: SQL schema and data insertion script
  - `init_database.py`: Script to initialize the SQLite database

## Database Contents

### Relational Database (SQLite)

**Customer Table**

```
customer_id (int, primary key)
name (string)
city (string)
```

10 sample customers from various cities.

### XML Database

**PurchaseOrders**

```xml
<PurchaseOrders>
  <PurchaseOrder>
    <order_id>...</order_id>
    <customer_id>...</customer_id>
    <amount>...</amount>
    <item>
      <item_name>...</item_name>
      <item_category>...</item_category>
    </item>
  </PurchaseOrder>
  ...
</PurchaseOrders>
```

17 sample purchase orders with items in Electronics and Furniture categories.

## Views Defined

### 1. HighValueCustomers

Finds customers with purchases exceeding amount > 10,000

**Query Logic:**

```
SELECT Customer.customer_id, Customer.name, Customer.city
FROM Customer, PurchaseOrder
WHERE Customer.customer_id = PurchaseOrder.customer_id
AND PurchaseOrder.amount > 10000
```

**XPath:** `/PurchaseOrders/PurchaseOrder[amount > 10000]`

### 2. CustomersByItem

Finds customers who purchased a specific item (Laptop)

**Query Logic:**

```
SELECT Customer.customer_id, Customer.name, Customer.city
FROM Customer, PurchaseOrder
WHERE Customer.customer_id = PurchaseOrder.customer_id
AND PurchaseOrder.item_name = 'Laptop'
```

**XPath:** `/PurchaseOrders/PurchaseOrder[item/item_name = 'Laptop']`

### 3. CustomerPurchases

Retrieves all purchases for a specific customer (customer_id = 5)

**XPath:** `/PurchaseOrders/PurchaseOrder[customer_id = '5']`

## Query Execution Flow

```
View Definition (XML)
        ↓
View Resolver (parse view_name)
        ↓
Query Planner (identify entities and filters)
        ↓
     ╭──────┬──────╮
     ↓      ↓
  XPath   SQL
  Query   Query  (parallel execution)
     ↓      ↓
Result Set from XML ──→ Extract customer_ids
     ↓
  Filter SQL by customer_ids
     ↓
SQL Result Set
     ↓
Equi-Join on customer_id
     ↓
Merged Result Table (flattened)
```

## Key Design Decisions

### 1. XPath vs Python Filtering

- ElementTree has limited XPath support (no complex predicates)
- Filters are applied using Python comparison operators post-query
- More flexible and readable

### 2. Type Conversion in Joins

- XML values are extracted as strings
- SQL values maintain their database types
- Join logic includes type conversion (e.g., '1' == 1)

### 3. BasePath Optimization

- MetaSchema stores `BasePath` for XML entities
- Attributes store relative XPath paths
- Full XPath = BasePath + attribute path
- Reduces redundancy and improves maintainability

### 4. Federated Query Model

- No data is copied between databases
- Queries execute on source systems
- Results filtered and joined in-memory
- Minimal network overhead

## Setup and Usage

### Prerequisites

- Python 3.7+
- sqlite3 (built-in)
- xml.etree (built-in)

### Initialization

1. **Create the dummy database:**

```bash
cd dummy_data
python3 init_database.py
```

This will:

- Create `customers.db` SQLite database
- Insert 10 sample customers
- Verify data integrity

2. **Verify the XML data:**
   The `purchaseorders.xml` file is ready to use. It contains 17 sample purchase orders.

### Running Queries

```bash
python3 query_engine.py
```

This executes the three predefined views and displays results.

### Custom Queries

To execute a custom view:

```python
from query_engine import MetaSchemaLoader, ViewLoader, QueryExecutor
import os

base_path = '/path/to/project'

# Load metadata
metaschema = MetaSchemaLoader(os.path.join(base_path, 'MetaSchema.xml'))
views = ViewLoader(os.path.join(base_path, 'views/views.xml'))

# Create executor
executor = QueryExecutor(metaschema, views,
    os.path.join(base_path, 'dummy_data/customers.db'),
    os.path.join(base_path, 'dummy_data/purchaseorders.xml'))

# Execute a view
results = executor.execute_view('HighValueCustomers')

for row in results:
    print(row)

executor.close()
```

## Sample Output

### HighValueCustomers View

Shows customers with purchases > 10,000 with merged data from both databases:

```
{
  'customer_id': '1',
  'name': 'Alice Johnson',
  'city': 'New York',
  'order_id': '101',
  'amount': '45000',
  'item_name': 'Laptop',
  'item_category': 'Electronics'
}
...
```

### Result Statistics

- **HighValueCustomers**: 10 purchase orders from 7 unique customers (all with amount > 10,000)
- **CustomersByItem**: 4 purchase orders from 4 customers who bought Laptops
- **CustomerPurchases**: All purchases for customer_id = 5

## File Structure

```
phase1/
├── MetaSchema.xml              # Global schema definition
├── metaMetaSchema.xml          # XSD schema for MetaSchema
├── views/
│   └── views.xml               # Logical view definitions
├── query_engine.py             # Main query execution engine
├── dummy_data/
│   ├── customers.db            # SQLite database
│   ├── purchaseorders.xml      # XML data file
│   ├── create_database.sql     # SQL schema and data
│   └── init_database.py        # Database initialization script
├── debug_xml_query.py          # Debug script for XML queries
├── debug_query_execution.py    # Debug script for full execution
└── README.md                   # This file
```

## Limitations and Simplifications

The current implementation supports:

- Single filter per view
- Equi-joins only
- One relational database
- One XML database
- Simple view definitions (no nested views)

These simplifications are intentional to keep the prototype manageable while demonstrating core concepts.

## Extension Points

Future enhancements could include:

- Multiple filters with AND/OR logic
- Complex joins (left, right, full outer)
- Multiple heterogeneous databases (JSON, CSV, etc.)
- Query optimization and caching
- XPath 2.0+ support via external libraries
- View composition and nested views

## Technologies Used

- **Python 3**: Core implementation language
- **SQLite**: Relational database engine
- **ElementTree**: XML parsing and XPath support
- **XML**: Schema and data formats

## References

- XPath specification: https://www.w3.org/TR/xpath/
- SQL: Standard Structured Query Language
- Federated Database Systems concepts
