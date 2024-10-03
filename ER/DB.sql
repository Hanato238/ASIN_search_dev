CREATE TABLE sellers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller VARCHAR(20) UNIQUE NOT NULL,
    is_good BOOLEAN DEFAULT FALSE
);

CREATE TABLE products_master (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asin VARCHAR(15) UNIQUE,
    weight FLOAT,
    weight_unit VARCHAR(10),
    image_url VARCHAR(255),
    last_search TIMESTAMP NOT NULL,
    ec_search BOOLEAN DEFAULT FALSE,
    is_good BOOLEAN DEFAULT FALSE,
    is_filled BOOLEAN DEFAULT FALSE
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
    price_unit VARCHAR(3),
    availability BOOLEAN,
    ec_url VARCHAR(255),
    is_filled BOOLEAN DEFAULT FALSE,
    is_supported BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (asin_id) REFERENCES products_master(id)
);

CREATE TABLE ec_sites (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ec_site VARCHAR(50) NOT NULL,
    cry VARCHAR(4),
    to_research BOOLEAN
);


CREATE TABLE products_detail (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asin_id BIGINT NOT NULL,
    ec_url_id BIGINT,
    product_price FLOAT,
    research_date TIMESTAMP,
    three_month_sales FLOAT,
    competitors INT,
    sales_price INT,
    commission INT,
    expected_import_fees FLOAT,
    expected_roi FLOAT,
    decision BOOLEAN,
    final_decision BOOLEAN,
    is_ec_searched BOOLEAN DEFAULT FALSE,
    is_researched BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (asin_id) REFERENCES products_master(id),
    FOREIGN KEY (ec_url_id) REFERENCES products_ec(id)
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



INSERT INTO ec_sites (ec_site, cry, to_research) VALUES
('https://www.amazon.com/', 'USD', True),
('https://www.walmart.com/', 'USD', True),
('https://www.ebay.com/', 'USD', True);