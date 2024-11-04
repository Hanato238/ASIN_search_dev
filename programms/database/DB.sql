CREATE TABLE seller (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller VARCHAR(20) UNIQUE NOT NULL,
    is_good BOOLEAN DEFAULT FALSE
);

CREATE TABLE master (
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

CREATE TABLE junction(
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller_id BIGINT,
    product_id BIGINT,
    FOREIGN KEY (seller_id) REFERENCES seller(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES master(id) ON DELETE CASCADE
);

CREATE TABLE ec (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    price FLOAT,
    currency VARCHAR(3),
    is_available BOOLEAN,
    ec_url VARCHAR(255),
    is_filled BOOLEAN DEFAULT FALSE,
    is_supported BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES master(id) ON DELETE CASCADE
);

CREATE TABLE ec_sites (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ec_site VARCHAR(50) NOT NULL,
    cry VARCHAR(4),
    to_research BOOLEAN
);


CREATE TABLE detail (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    ec_id BIGINT,
    purchase_price FLOAT,
    research_date TIMESTAMP,
    three_month_sales FLOAT,
    competitors INT,
    sales_price INT,
    commission INT,
    import_fees FLOAT,
    roi FLOAT,
    decision BOOLEAN,
    final_decision BOOLEAN,
    is_filled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES master(id) ON DELETE CASCADE,
    FOREIGN KEY (ec_id) REFERENCES ec(id) ON DELETE CASCADE
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