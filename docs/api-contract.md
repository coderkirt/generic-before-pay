# Generic Before Pay — REST API Contract

Version: `v1`  
Base URL: `/api/v1`

---

## 1. Global Specifications

### Headers
- `Content-Type: application/json`
- `Accept: application/json`

### Disclaimer Requirement
Every 2xx response that delivers drug pricing or molecule data must include the standard safety disclaimer:
```json
"disclaimer": "This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything."
```

### Safety Field Policy
No endpoint shall output or accept dosage, frequency, administration schedule, or clinical substitution recommendations.

### Standard Error Response Shape
All error responses adhere to the unified format:
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Drug with id 'xyz-123' was not found.",
    "details": null
  }
}
```

Standard error codes:
- `INVALID_QUERY`: Missing or empty query parameter.
- `RESOURCE_NOT_FOUND`: Specified drug ID does not exist in dataset.
- `VALIDATION_ERROR`: Malformed request payload.
- `SERVER_ERROR`: Internal server processing failure.

---

## 2. Endpoints

### 2.1 Fuzzy Search
Search for drugs by brand name, partial name, or molecule name with typo tolerance. Returns top candidates with confidence scores. Never auto-selects or auto-substitutes.

- **Method**: `GET`
- **Path**: `/search`
- **Query Parameters**:
  - `q` (string, required): Search term (e.g., `"calpol"`, `"dolo 650"`, `"metformin"`)
  - `limit` (integer, optional, default: 3, max: 10): Maximum number of candidates to return.

#### Response: `200 OK`
```json
{
  "success": true,
  "data": {
    "query": "clpol",
    "total_matches": 1,
    "matches": [
      {
        "id": "paracetamol-500mg-tab",
        "brand_name": "Calpol 500",
        "molecule": "Paracetamol",
        "strength": "500 mg",
        "unit": "strip of 10 tablets",
        "branded_price": 32.50,
        "generic_price": 5.00,
        "savings_amount": 27.50,
        "savings_percentage": 84.6,
        "confidence_score": 0.89,
        "match_type": "fuzzy_brand"
      }
    ]
  },
  "disclaimer": "This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything."
}
```

---

### 2.2 Drug Detail
Fetch complete pricing, active molecule, and source details for a specific drug.

- **Method**: `GET`
- **Path**: `/drugs/{id}`
- **Path Parameters**:
  - `id` (string, required): Stable drug ID (e.g., `"paracetamol-500mg-tab"`)

#### Response: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": "paracetamol-500mg-tab",
    "brand_name": "Calpol 500",
    "molecule": "Paracetamol",
    "strength": "500 mg",
    "unit": "strip of 10 tablets",
    "branded_price": 32.50,
    "generic_price": 5.00,
    "savings_amount": 27.50,
    "savings_percentage": 84.6,
    "source": "PMBJP Price List Sep 2024 / NPPA",
    "generic_equivalent_name": "Paracetamol Tablets IP 500mg (Jan Aushadhi)"
  },
  "disclaimer": "This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything."
}
```

#### Response: `404 Not Found`
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Drug with id 'unknown-id' was not found.",
    "details": null
  }
}
```

---

### 2.3 Compare / Prescription Savings Calculator
Calculate per-item savings and aggregate prescription savings for a basket of chosen medicines.

- **Method**: `POST`
- **Path**: `/compare`
- **Request Body**:
```json
{
  "items": [
    {
      "id": "paracetamol-500mg-tab",
      "quantity": 2
    },
    {
      "id": "metformin-500mg-tab",
      "quantity": 1
    }
  ]
}
```

#### Response: `200 OK`
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_items": 2,
      "total_units": 3,
      "total_branded_cost": 93.00,
      "total_generic_cost": 15.00,
      "total_savings": 78.00,
      "overall_savings_percentage": 83.9,
      "currency": "INR"
    },
    "breakdown": [
      {
        "id": "paracetamol-500mg-tab",
        "brand_name": "Calpol 500",
        "molecule": "Paracetamol",
        "strength": "500 mg",
        "unit": "strip of 10 tablets",
        "quantity": 2,
        "branded_unit_price": 32.50,
        "generic_unit_price": 5.00,
        "branded_total_price": 65.00,
        "generic_total_price": 10.00,
        "item_savings": 55.00,
        "savings_percentage": 84.6
      },
      {
        "id": "metformin-500mg-tab",
        "brand_name": "Glycomet 500",
        "molecule": "Metformin Hydrochloride",
        "strength": "500 mg",
        "unit": "strip of 10 tablets",
        "quantity": 1,
        "branded_unit_price": 28.00,
        "generic_unit_price": 5.00,
        "branded_total_price": 28.00,
        "generic_total_price": 5.00,
        "item_savings": 23.00,
        "savings_percentage": 82.1
      }
    ]
  },
  "disclaimer": "This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything."
}
```

---

### 2.4 Data Version (Offline Sync Checker)
Enables clients to check whether local offline cached bundles need updating without downloading full datasets.

- **Method**: `GET`
- **Path**: `/data/version`

#### Response: `200 OK`
```json
{
  "success": true,
  "data": {
    "schema_version": "1.0.0",
    "dataset_version": "2026.10.1",
    "dataset_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "total_records": 25,
    "last_updated": "2026-10-21T00:00:00Z"
  }
}
```

---

### 2.5 Data Bundle (Offline Cache Sync)
Delivers the complete curated drug dataset for local in-app caching and client-side offline fuzzy search.

- **Method**: `GET`
- **Path**: `/data/bundle`
- **Headers (Optional)**:
  - `If-None-Match`: `"<etag_or_hash>"`

#### Response: `200 OK`
```json
{
  "success": true,
  "metadata": {
    "version": "2026.10.1",
    "dataset_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "record_count": 25,
    "last_updated": "2026-10-21T00:00:00Z"
  },
  "drugs": [
    {
      "id": "paracetamol-500mg-tab",
      "brand_name": "Calpol 500",
      "molecule": "Paracetamol",
      "strength": "500 mg",
      "unit": "strip of 10 tablets",
      "branded_price": 32.50,
      "generic_price": 5.00,
      "source": "PMBJP Sep 2024 / NPPA",
      "aliases": ["calpol", "crocin", "paracip"]
    }
  ],
  "disclaimer": "This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything."
}
```

#### Response: `304 Not Modified`
Returned if client `If-None-Match` matches the current dataset hash.
