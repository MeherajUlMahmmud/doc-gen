# Template Creation Guideline

This guide explains how to create document templates for the Document Generation System.

## Overview

Templates are Microsoft Word (.docx) files that contain placeholders which are automatically replaced with user-provided data when generating documents. The system parses these placeholders and creates dynamic forms for users to fill in.

## Template File Requirements

- **Format**: Microsoft Word Document (.docx) format only
- **File Size**: Up to 10MB
- **Location**: Upload via the admin interface at `/templates/upload/`

## Placeholder Syntax

Placeholders use the following format:

```
{{variable_name|field_type|label|validation}}
```

### Placeholder Components

1. **Variable Name** (required): The unique identifier for the field
   - Use lowercase letters, numbers, and underscores
   - Examples: `name`, `email_address`, `date_of_birth`
   - Must be unique within the template

2. **Field Type** (optional, default: `text`): Determines the input type
   - Available types: `text`, `number`, `checkbox`, `signature`
   - Default: `text` if not specified

3. **Label** (optional): Display name shown in the form
   - If not provided, the variable name is converted to a readable format
   - Example: `first_name` becomes "First Name"

4. **Validation** (optional): Additional validation rules
   - Multiple rules can be combined
   - See validation section below for details

## Field Types

### 1. Text Field
```
{{name|text|Full Name|required}}
{{email|text|Email Address}}
{{address|text|Street Address|required}}
```

**Usage**: Standard text input fields for names, addresses, descriptions, etc.

### 2. Number Field
```
{{age|number|Age|min:18|max:100}}
{{quantity|number|Quantity|required|min:1}}
{{price|number|Price|min:0}}
```

**Usage**: Numeric values with optional min/max constraints.

**Validation Options**:
- `min:value` - Minimum allowed value
- `max:value` - Maximum allowed value
- `required` - Field must be filled

### 3. Checkbox Field
```
{{terms_accepted|checkbox|I accept the terms|required}}
{{newsletter|checkbox|Subscribe to newsletter}}
```

**Usage**: Boolean yes/no fields. Values are displayed as "Yes" or "No" in the generated document.

### 4. Signature Field
```
{{signature|signature|Signature|required}}
{{approver_signature|signature|Approver Signature}}
```

**Usage**: Special field that can be replaced with a signature image during document approval. The signature image is uploaded by the user in their profile.

**Note**: Signature fields require the user to have uploaded a signature image and entered their PIN during the approval process.

### 5. Dropdown/Select Field
```
{{country|text|Country|required|options:USA,Canada,Mexico,UK}}
{{status|text|Status|options:Draft,Review,Approved}}
{{department|text|Department|options:Sales,Marketing,IT,HR}}
```

**Usage**: Creates a dropdown menu with predefined options.

**Validation**: Use `options:value1,value2,value3` to define selectable options.

## Validation Rules

Validation rules are specified in the fourth component of the placeholder:

### Required Field
```
{{name|text|Full Name|required}}
```
Makes the field mandatory - users must fill it before generating the document.

### Options (Dropdown)
```
{{country|text|Country|options:USA,Canada,Mexico,UK,Other}}
```
Creates a dropdown with the specified options. Options are comma-separated.

### Min/Max Values (for numbers)
```
{{age|number|Age|min:18|max:100}}
{{quantity|number|Quantity|min:1|max:1000}}
```
Sets minimum and/or maximum values for number fields.

### Combining Validation Rules
```
{{email|text|Email|required}}
{{age|number|Age|required|min:18|max:100}}
{{country|text|Country|required|options:USA,Canada,Mexico}}
```

## Template Examples

### Example 1: Simple Letter Template

```
Date: {{date|text|Date|required}}

Dear {{recipient_name|text|Recipient Name|required}},

This letter is regarding {{subject|text|Subject|required}}.

{{body_text|text|Body Text|required}}

Sincerely,
{{sender_name|text|Sender Name|required}}
{{signature|signature|Signature}}
```

### Example 2: Form with Tables

You can use placeholders in tables:

```
| Field          | Value                    |
|----------------|--------------------------|
| Name           | {{name|text|Name}}       |
| Email          | {{email|text|Email}}     |
| Age            | {{age|number|Age|min:18}} |
| Country        | {{country|text|Country|options:USA,Canada,Mexico}} |
| Terms Accepted | {{terms|checkbox|Terms Accepted|required}} |
```

### Example 3: Contract Template

```
CONTRACT AGREEMENT

Party A: {{party_a_name|text|Party A Name|required}}
Party B: {{party_b_name|text|Party B Name|required}}

Effective Date: {{effective_date|text|Effective Date|required}}

Terms and Conditions:
{{terms|text|Terms and Conditions|required}}

Amount: ${{amount|number|Amount|required|min:0}}

This contract is valid for {{duration|number|Duration (months)|required|min:1|max:120}} months.

Approved by:

Party A Signature: {{party_a_signature|signature|Party A Signature|required}}
Date: {{party_a_date|text|Date|required}}

Party B Signature: {{party_b_signature|signature|Party B Signature|required}}
Date: {{party_b_date|text|Date|required}}
```

## Best Practices

### 1. Naming Conventions
- Use descriptive variable names: `first_name` instead of `fn`
- Use lowercase with underscores: `date_of_birth` not `DateOfBirth`
- Be consistent: `email_address` vs `email` - pick one style

### 2. Required Fields
- Mark essential fields as `required`
- Don't overuse required fields - only for truly necessary information

### 3. Labels
- Always provide clear, user-friendly labels
- Example: `{{dob|text|Date of Birth|required}}` is better than `{{dob|text|DOB|required}}`

### 4. Validation
- Use appropriate validation for each field type
- Set reasonable min/max values for numbers
- Provide comprehensive options for dropdowns

### 5. Template Structure
- Use proper Word formatting (headings, paragraphs, tables)
- Keep placeholders on single lines when possible
- Test your template after uploading

### 6. Signature Fields
- Place signature fields at the end of documents
- Include date fields near signatures
- Consider adding signature labels (e.g., "Signature:" before the placeholder)

### 7. Tables
- Placeholders work in table cells
- Ensure table structure is clear and readable
- Test that placeholders don't break table formatting

## Formatting Support

The system supports HTML formatting in field values. When users enter HTML in rich text fields, it will be converted to formatted text in the document:

- **Bold**: `<b>text</b>` or `<strong>text</strong>`
- **Italic**: `<i>text</i>` or `<em>text</em>`
- **Underline**: `<u>text</u>`
- **Strikethrough**: `<s>text</s>` or `<del>text</del>`
- **Colors**: `<span style="color: #ff0000">text</span>`
- **Background Colors**: `<span style="background-color: #ffff00">text</span>`

**Note**: HTML formatting is only applied if the field value contains HTML tags. Plain text fields will display as-is.

## Template Versioning

- Templates support versioning - upload a new version with the same title to create a new version
- Previous versions are preserved and can be viewed
- Users always use the latest version when generating documents
- Old generated documents retain their original template version

## Common Issues and Solutions

### Issue: Placeholder not appearing in form
**Solution**: Check the placeholder syntax - ensure it uses double curly braces `{{}}` and proper pipe separators `|`

### Issue: Field not showing as required
**Solution**: Ensure `required` is in the validation section (4th component) of the placeholder

### Issue: Dropdown not working
**Solution**: Check the options format - must be `options:value1,value2,value3` with no spaces around commas

### Issue: Number validation not working
**Solution**: Ensure min/max values are specified as `min:value` and `max:value` (not `min=value`)

### Issue: Signature not appearing
**Solution**: 
- Ensure the field type is `signature`
- User must have uploaded a signature image in their profile
- Document must go through the approval process

### Issue: HTML formatting not working
**Solution**: HTML tags must be properly formatted. The system supports basic HTML tags listed above.

## Testing Your Template

1. **Upload the template** via the admin interface
2. **Check the form** - verify all fields appear correctly
3. **Test validation** - try submitting without required fields
4. **Generate a document** - ensure all placeholders are replaced
5. **Check formatting** - verify tables, paragraphs, and formatting are preserved
6. **Test signatures** - if using signature fields, test the approval workflow

## Export Formats

Templates can be exported in three formats:
- **DOCX**: Microsoft Word format (recommended)
- **PDF**: Portable Document Format
- **DOC**: Legacy Word format (converted from DOCX)

**Note**: PDF export may have some formatting limitations compared to DOCX.

## Advanced Tips

1. **Reusing Variables**: If you use the same variable name multiple times, all instances will be replaced with the same value
2. **Conditional Logic**: Currently not supported - all placeholders are replaced with provided values
3. **Calculations**: Not supported - use static values or calculate externally
4. **Images**: Currently only signature images are supported
5. **Complex Formatting**: Preserve Word formatting in your template - it will be maintained in generated documents
