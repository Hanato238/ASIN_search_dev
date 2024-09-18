CREATE TABLE sellers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller VARCHAR(255) UNIQUE NOT NULL,
    is_good BOOLEAN
);

CREATE TABLE products_master (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asin VARCHAR(255) UNIQUE,
    weight FLOAT,
    weight_unit VARCHAR(255),
    image_url VARCHAR(255),
    last_search TIMESTAMP NOT NULL,
    is_good BOOLEAN
);

CREATE TABLE junction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller_id BIGINT,
    product_id BIGINT,
    FOREIGN KEY (seller_id) REFERENCES sellers(id),
    FOREIGN KEY (product_id) REFERENCES products_master(id)
);

CREATE TABLE products_ec (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asin_id BIGINT NOT NULL,
    price FLOAT,
    ec_url VARCHAR(255),
    FOREIGN KEY (asin_id) REFERENCES products_master(id)
);

CREATE TABLE ec_sites (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ec_site VARCHAR(255) NOT NULL,
    to_research BOOLEAN
);

CREATE TABLE products_detail (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asin_id BIGINT NOT NULL,
    ec_url_id BIGINT,
    price_jpy FLOAT,
    research_date TIMESTAMP,
    three_month_sales FLOAT,
    competitors INT,
    monthly_sales_per_competitor FLOAT,
    lowest_price INT,
    commission INT,
    deposit INT,
    expected_purchase_price FLOAT,
    expected_profit FLOAT,
    expected_roi FLOAT,
    decision BOOLEAN,
    final_decision BOOLEAN,
    FOREIGN KEY (asin_id) REFERENCES products_master(id),
    FOREIGN KEY (ec_url_id) REFERENCES ec_sites(id)
);



INSERT INTO sellers (seller) VALUES
('A3HXGR7WW6TCZU'),
('A3UER180TVRC81'),
('A31Q4BEULXEJD4'),
('A213BDSUMXMR5'),
('A3LDT7M6J1OZUH'),
('A28BFN20WKZJRU'),
('A2F3O09R621N7L'),
('A2I0XHD58EM6DE'),
('A2NL3Y3Y7U50YS');



INSERT INTO ec_sites (ec_site, to_research) VALUES
('https://www.amazon.com/', True),
('https://www.walmart.com/', True),
('https://www.ebay.com/', True)