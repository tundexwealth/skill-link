# Provider Import Workflow

## Remaining work items

### 3. Make provider records importable without user accounts
- [x] Add a backend path for imported seed providers
- [x] Keep imported providers distinct from user-created providers
- [ ] Verify manual provider registration still functions
- [ ] Verify imported records can be created without breaking auth logic

### 4. Add source/metadata for imported records
- [x] Add `is_imported` and `imported_from`
- [x] Add `verified` / `verification_status` support in API responses
- [x] Tag seed data from `backend/seed/seed.py` as imported from `seed`
- [ ] Verify admin and provider endpoints still behave
- [ ] Verify UI can show “Imported data” or “Not verified”

> Seed folder CSV is available at `backend/seed/Free Nigeria Business List export 2026-08-04 22-44-59.csv` and should be used for later import/deduplication work.

### 5. Normalize CSV fields into your schema
- [ ] Map `industry` → app category
- [ ] Map `locality` / `region` → Location.city / Location.state
- [ ] Map `website` → provider contact
- [ ] Verify categories remain consistent
- [ ] Verify location data stores correctly
- [ ] Verify no duplicate categories are created

### 6. Add import/deduplication logic
- [ ] Detect duplicates by name + locality, name + website, or name + email
- [ ] Avoid importing the same business twice
- [ ] Verify CSV import does not create duplicate providers
- [ ] Verify manual entries still work

### 7. Add a robust search/filter API
- [ ] Search providers by category/industry, location/city/state, business name
- [ ] Add filters for verified providers and providers with website/contact info
- [ ] Verify current category/service listing endpoints still work
- [ ] Verify new search endpoint returns accurate results

### 8. Add provider detail and listing pages
- [ ] Provide a detail view for each provider
- [ ] Surface business name, location, phone, website, email, description/about, average rating, reviews
- [ ] Verify listing page renders without breaking existing HTML
- [ ] Verify provider detail page uses correct contact data

### 9. Add rating UX improvements
- [ ] Ensure rating is tied to Provider
- [ ] Keep existing create/update rating flow
- [ ] Optionally add rating validation (no self-rating), rating count / average score
- [ ] Verify rating endpoint continues working
- [ ] Verify ratings display correctly in provider detail

### 10. Add provider claim/update workflow
- [ ] Allow a real business owner to claim an imported listing
- [ ] Provide a safe way to update imported provider data
- [ ] Verify claim flow does not break imported provider records
- [ ] Verify user-auth flow still works

### 11. Add enrichment and maintenance tools
- [ ] Add a script or admin page to update missing phone/email, fill missing descriptions, replace poor website links
- [ ] Verify seed import remains stable
- [ ] Verify manual data updates do not break existing providers

### 12. Add startup-friendly product polish
- [ ] Add featured or trusted badges for verified providers
- [ ] Add contact CTA buttons: Call, Visit Website, Email
- [ ] Add search suggestions or category cards
- [ ] Verify UI remains stable
- [ ] Verify new UX elements do not break older pages
