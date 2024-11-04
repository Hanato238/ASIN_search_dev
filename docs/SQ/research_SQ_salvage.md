```mermaid

---
sequenceDiagram
    actor user as Users
    participant db as Database
    participant cf as CloudFunctions

        op salvage products and modify positive list
        cf ->> db : request product_id at junction with ec_site NULL and seller(is_good) == 1
        db -->> cf : return product_id
        cf ->> user : image search widely by product_id
        user ->> db : check the ec site

