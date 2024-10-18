
```mermaid

---
title: "商品リサーチDB(案)"
---
erDiagram
    sellers ||--o{ junc_market : "① ASINリスト取得"
    junc_market }o--|| master : "② 商品マスタ情報取得"
    detail }o--|| sellers : ""
    master ||--o{ detail : "④ サーチリスト作成"
    master ||--o{ ec : "③ 画像で仕入れ先候補検索"
    detail ||--|| ec_sites : "検索元サイト"
    master ||--o{ junc_purchase
    junc_purchase }o--|| purchase
    purchase ||--o{ junc_stock_abroad
    junc_stock_abroad }o--|| stock_abroad
    stock_abroad ||--o{ junc_stock_japan
    junc_stock_japan }o--|| stock_japan



    sellers {
        bigint id PK "auto increment"
        varchar seller UK "Seller ID: not null"
        bool is_good "継続的な検索対象にするか"
    }

    master { 
        bigint id PK "auto increment"
        varchar asin UK "ASIN: not null"
        float weight "商品重量"
        varchar weight_unit "重量単位: [kilograms, grams, pound, onuce]"
        string image_url "商品画像URL"
        timestamp last_search "最終検索日時: not null"
        bool ec_search "image_urlでサーチ済みか: default FALSE"
        bool is_good "継続的な検索対象にするか: default FALSE"
        bool is_filled "SP-APIでサーチ済みか: default FALSE"
    }

    junc_market {
        bigint id PK "ID: auto increment"
        bigint seller_id FK "sellers.id"
        bigint product_id FK "master.id"
    }

    ec {
        bigint id PK "auto increment"
        bigint product_id FK "master.id: not null"
        int price
        string currency
        bool is_available "仕入れ可能か"
        string ec_url "仕入れ先候補URL"
        bool is_filled "scrape済か: default FALSE"
        bool is_supported "scrapeできるサイトか: default FALSE"

    }

%%いる？orクラス内変数
    ec_sites {
        int id PK "auto increment"
        string ec_site "検索元URL: not null"
        bool to_research "0-not, 1-research"
    }

    detail {
        bigint id PK "auto increment"
        bigint product_id FK "master.id: not null"
        bitint ec_id FK "ec.id"
        float purchase_price "仕入れ価格(JPY)"
        timestamp research_date "リサーチ日時"
        float three_month_sales "3カ月間販売数"
        int competitors "競合数"
        int sales_price "競合最低出品価格"
        int commission "FBA手数料"
        float import_fees "予想仕入値"
        float roi "予想利益率"
        bool decision "仕入判定: default FALSE"
        bool final_dicision "最終判定: default FALSE"
        bool is_filled "Keepa-APIで検索済みか: default FALSE"
    }

    junc_purchase {
        bigint id PK "auto increment"
        bigint product_id FK "master.id: not null"
        bitint purchase_id FK "purchase.id: not null
        int quantity "仕入れ数"
        float price "購入単価"
        float currency "通貨"
        string currency "購入通貨"
        float transfer_fee "配送料"
    }

    purchase {
        bigint id PK "auto increment"
        boolean is_transferred "転送状況: default FALSE"
    }

    junc_stock_abroad {
        bigint id PK "auto increment"
        bigint purchase_id FK "purchase.id: not null"
        bigint stock_abroad_id FK "stock_abroad.id: not null"
    }

    %% stock_local
    stock_abroad {
        bigint id PK "auto increment"
        varchar place "海外倉庫 or 転送業者"
        timestamp arrival_date "到着日時"
        timestamp shipping_date "転送日時"
        float import_tax "関税"
        float transfer_fee "納品手数料"
        boolean is_transferred "転送状況: default FALSE"
    }

    junc_stock_japan {
        bigint id PK "auto incremane"
        bigint stock_abroad_id FK "stock_abroad.id: not null"
        bigint stock_japan_id FK "stock_japan.id: not null"
    }

    %% stock_destination or stock_marketplace
    stock_japan {
        bigint id PK "在庫ID"
        varchar place "転送業者"
        timestamp arrival_date "到着日時"
        timestamp created_date "納品日時
        int quantity "在庫数"
        int sales "販売数"
        boolean is_transferred "納品状況: default FALSE"
    }

    %% stock_market
    stock_amazon {
        bigint id PK "出荷ID"
        timestamp arrival_date "到着日時"
        timestamp transfer_date "出荷日時"
        int quantity "販売数"
        int sales_price "価格"
        string currency "通貨"
        int profit "利益"
    }

    analysis {
        bigint id PK "分析ID"
        varchar asin FK "ASIN:junc_market.asin"
        float three_month_roi "過去3カ月利益率"
        boolean restock_dicision "再入荷判定"
    }


```