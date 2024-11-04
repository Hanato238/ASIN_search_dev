```mermaid
---
title: '商品マスタ情報検索'
---
sequenceDiagram
    participant db as Database
    participant cf as CloudFunctions
    participant spapi as SP-API

        opt 定期実行 : 商品マスタ検索
            cf ->> db : request ASIN at products_master(weight=NULL)
            db -->> cf : return ASIN
            cf ->> spapi : search by ASIN
            spapi -->> cf : return details
            cf -->> db : write details at products_master
        end
```
