# Airtable Setup Instructions for Applicant Tracking System

## Overview
This document provides complete instructions for setting up the Airtable base that supports the Applicant Tracking System application.

## Step 1: Create New Airtable Base

1. Log into your Airtable account at https://airtable.com
2. Click **"Create a base"** 
3. Choose **"Start from scratch"**
4. Name your base: **"Applicant Tracking System"**
5. Choose a color/icon for your base

## Step 2: Create Tables and Fields

### Table 1: Applicants (Main table)

**Purpose**: Central table storing applicant records and processing status

**Fields to create**:
1. **Applicant ID** (Primary Field)
   - Type: AutoNumber
   - Description: Unique identifier for each applicant

2. **Compressed JSON**
   - Type: Long text
   - Description: Stores compressed applicant data

3. **LLM Summary** 
   - Type: Long text
   - Description: AI-generated summary of applicant qualifications

4. **LLM Score**
   - Type: Number
   - Number format: Decimal (0.0)
   - Description: AI-generated score from 0-10

5. **Status**
   - Type: Single select
   - Options: Pending, Processed, Error
   - Default: Pending
   - Description: Processing status of the application

6. **Last Hash**
   - Type: Long text
   - Description: Hash for change detection (hidden from views)

---

### Table 2: Personal Details

**Purpose**: Store applicant personal information

**Fields to create**:
1. **Personal Details ID** (Primary Field)
   - Type: AutoNumber

2. **Full Name**
   - Type: Single line text
   - Required: Yes
   - Description: Applicant's full name

3. **Email**
   - Type: Email
   - Required: Yes
   - Description: Contact email address

4. **Location** 
   - Type: Single line text
   - Description: City, state/country location

5. **LinkedIn**
   - Type: URL
   - Description: LinkedIn profile URL

6. **Applicant ID**
   - Type: Link to another record
   - Link to: Applicants table
   - Description: Links to main applicant record

7. **Inactive**
   - Type: Checkbox
   - Default: Unchecked
   - Description: Used for soft-delete functionality

---

### Table 3: Work Experience

**Purpose**: Store applicant work history

**Fields to create**:
1. **Experience ID** (Primary Field)
   - Type: AutoNumber

2. **Company**
   - Type: Single line text
   - Description: Company name

3. **Title**
   - Type: Single line text
   - Description: Job title/position

4. **Start**
   - Type: Date
   - Date format: YYYY-MM
   - Description: Start date

5. **End**
   - Type: Date  
   - Date format: YYYY-MM
   - Description: End date (empty if current)

6. **Technologies**
   - Type: Multiple select
   - Options: Python, JavaScript, React, Node.js, AWS, Docker, MongoDB, PostgreSQL, Java, C++, Go, Rust, TypeScript, Vue.js, Angular, Kubernetes, Redis, GraphQL, REST APIs, Machine Learning, DevOps, CI/CD, Git, Linux, Agile, Scrum
   - Color-coded options recommended
   - Description: Technologies used in this role

7. **Applicant ID**
   - Type: Link to another record
   - Link to: Applicants table
   - Description: Links to main applicant record

8. **Inactive**
   - Type: Checkbox
   - Default: Unchecked
   - Description: Used for soft-delete functionality

---

### Table 4: Salary Preferences

**Purpose**: Store applicant compensation preferences

**Fields to create**:
1. **Salary ID** (Primary Field)
   - Type: AutoNumber

2. **Preferred Rate**
   - Type: Currency or Number
   - Format: USD, no decimals
   - Description: Desired hourly rate

3. **Min Rate**
   - Type: Currency or Number
   - Format: USD, no decimals
   - Description: Minimum acceptable hourly rate

4. **Currency**
   - Type: Single select
   - Options: USD, EUR, GBP, CAD, AUD, CHF, SEK, NOK, DKK
   - Default: USD
   - Description: Currency for rates

5. **Availability**
   - Type: Number
   - Number format: Integer
   - Description: Available hours per week

6. **Applicant ID**
   - Type: Link to another record
   - Link to: Applicants table
   - Description: Links to main applicant record

7. **Inactive**
   - Type: Checkbox
   - Default: Unchecked
   - Description: Used for soft-delete functionality

---

### Table 5: Shortlisted Leads

**Purpose**: Store candidates who meet shortlisting criteria

**Fields to create**:
1. **Lead ID** (Primary Field)
   - Type: AutoNumber

2. **Applicant**
   - Type: Link to another record
   - Link to: Applicants table
   - Description: Reference to original applicant

3. **Compressed JSON**
   - Type: Long text
   - Description: Copy of applicant data at time of shortlisting

4. **Score**
   - Type: Number
   - Number format: Integer
   - Description: Total shortlisting score

5. **Score Reason**
   - Type: Long text
   - Description: Breakdown of why applicant was shortlisted

6. **Created At**
   - Type: Date and time
   - Description: When the applicant was shortlisted

---

### Table 6: Shortlist Rules

**Purpose**: Configure dynamic shortlisting criteria

**Fields to create**:
1. **Rule ID** (Primary Field)
   - Type: AutoNumber

2. **Criterion**
   - Type: Single select
   - Options: experience, compensation, location, technology, availability, education
   - Description: Category of the rule

3. **Rule**
   - Type: Single line text
   - Description: Rule logic (e.g., ">=4 years", "<=$100/hr")

4. **Points**
   - Type: Number
   - Number format: Integer
   - Default: 1
   - Description: Points awarded if rule matches

5. **Active**
   - Type: Checkbox
   - Default: Checked
   - Description: Whether this rule is currently active

6. **Description**
   - Type: Long text
   - Description: Human-readable explanation of the rule

---

### Table 7: LLM History (Optional)

**Purpose**: Track LLM evaluation history and versioning

**Fields to create**:
1. **History ID** (Primary Field)
   - Type: AutoNumber

2. **Applicant ID**
   - Type: Link to another record
   - Link to: Applicants table

3. **Summary**
   - Type: Long text
   - Description: LLM-generated summary

4. **Score**
   - Type: Number
   - Number format: Decimal (0.0)
   - Description: LLM score 0-10

5. **Follow Up Questions**
   - Type: Long text
   - Description: JSON array of suggested questions

6. **Data Hash**
   - Type: Single line text
   - Description: Hash of input data

7. **Provider**
   - Type: Single select
   - Options: openai, anthropic
   - Description: LLM provider used

8. **Model**
   - Type: Single line text
   - Description: Specific model used

9. **Tokens Used**
   - Type: Number
   - Number format: Integer
   - Description: Estimated token consumption

10. **Success**
    - Type: Checkbox
    - Description: Whether evaluation succeeded

11. **Error Message**
    - Type: Long text
    - Description: Error details if evaluation failed

12. **Timestamp**
    - Type: Date and time
    - Description: When evaluation occurred

## Step 3: Set Up Sample Shortlist Rules

Add these initial records to the **Shortlist Rules** table:

| Criterion | Rule | Points | Active | Description |
|-----------|------|---------|--------|-------------|
| experience | >=3 years | 1 | ✓ | At least 3 years total experience |
| compensation | <=$100/hr | 1 | ✓ | Hourly rate under $100 |
| location | US only | 1 | ✓ | Located in United States |
| availability | >=35 hours | 1 | ✓ | Full-time availability |
| technology | has Python | 1 | ✓ | Experience with Python |
| technology | has React | 1 | ✓ | Experience with React |

## Step 4: Configure Views

### Applicants Table Views:
1. **All Applications** (default grid view)
2. **Pending Processing** (filter: Status = "Pending")
3. **Processed Applications** (filter: Status = "Processed")
4. **Processing Errors** (filter: Status = "Error")

### Shortlisted Leads Views:
1. **All Shortlisted** (default, sorted by Score desc)
2. **High Scorers** (filter: Score >= 3)
3. **Recent Shortlisted** (sorted by Created At desc)

## Step 5: Set Up Permissions

1. **Admin Role**: Full edit access to all tables
2. **Viewer Role**: Read-only access to Shortlisted Leads and summary views
3. **Form User Role**: Create-only access for application submissions

## Step 6: Get API Credentials

1. Go to https://airtable.com/create/tokens
2. Create a new personal access token
3. Give it a descriptive name: "Applicant Tracking System"
4. Add these scopes:
   - `data.records:read`
   - `data.records:write` 
   - `schema.bases:read`
5. Add your base to the token access
6. Copy the generated token (starts with `pat`)

## Step 7: Get Base ID

1. Go to https://airtable.com/api
2. Select your "Applicant Tracking System" base
3. Copy the Base ID from the URL or API documentation
4. It should start with `app` (e.g., `appABC123456789`)

## Step 8: Update Application Configuration

Update your `.env` file with the real credentials:

```bash
AIRTABLE_API_KEY=your_personal_access_token_here
AIRTABLE_BASE_ID=your_base_id_here
```

## Step 9: Test the Setup

1. Restart your Docker containers:
   ```bash
   docker compose down && docker compose up -d
   ```

2. Check the health endpoint:
   ```bash
   curl http://localhost:5000/api/health
   ```

3. If successful, you should see:
   ```json
   {
     "status": "healthy",
     "airtable": "connected",
     "redis": "connected",
     "llm_provider": "openai"
   }
   ```

## Troubleshooting

**Common Issues:**

1. **403 Forbidden**: Check that your API token has the right scopes
2. **404 Not Found**: Verify your Base ID is correct
3. **Table not found**: Ensure table names match exactly (case-sensitive)
4. **Field not found**: Verify all field names match the schema above

**Useful Airtable API Testing:**

```bash
# Test base access
curl "https://api.airtable.com/v0/YOUR_BASE_ID/Applicants?maxRecords=1" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Test record creation
curl -X POST "https://api.airtable.com/v0/YOUR_BASE_ID/Applicants" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"Status": "Pending"}}'
```

## Security Notes

- Never commit API keys to version control
- Use environment variables for all sensitive data
- Consider using Airtable's built-in access controls
- Regularly rotate API tokens
- Monitor API usage to prevent abuse

---

## Next Steps

Once your Airtable base is set up:

1. Test form submissions through the web interface
2. Verify data compression and LLM evaluation
3. Adjust shortlisting rules as needed
4. Set up monitoring and backup procedures
5. Train users on the admin dashboard

The application will now be fully functional with your Airtable backend!