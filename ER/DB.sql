CREATE TABLE sellers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller VARCHAR(255) UNIQUE NOT NULL,
    seller_name VARCHAR(255),
    shop_url VARCHAR(255),
    five_star_rate INT,
    last_search TIMESTAMP NOT NULL
);

CREATE TABLE products_master (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asin VARCHAR(255) UNIQUE,
    amazon_url VARCHAR(255),
    weight FLOAT,
    weight_unit VARCHAR(255),
    image VARCHAR(255),
    ec_url VARCHAR(255),
    unit_price FLOAT,
    cry VARCHAR(3),
    last_search TIMESTAMP NOT NULL,
    last_sellers_search TIMESTAMP NOT NULL
);

CREATE TABLE junction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller_id BIGINT,
    product_id BIGINT,
    evaluate BOOLEAN,
    product_master BOOLEAN,
    FOREIGN KEY (seller_id) REFERENCES sellers(id),
    FOREIGN KEY (product_id) REFERENCES products_master(id)
);

CREATE TABLE research (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    asin_id BIGINT NOT NULL,
    research_date TIMESTAMP,
    dicision BOOLEAN,
    final_dicision BOOLEAN,
    FOREIGN KEY (asin_id) REFERENCES products_master(id)
);


INSERT INTO sellers (seller, last_search) VALUES
('A3HXGR7WW6TCZU', '2020-01-01 00:00:00'),
('A3UER180TVRC81', '2020-01-01 00:00:00'),
('A31Q4BEULXEJD4', '2020-01-01 00:00:00'),
('A213BDSUMXMR5', '2020-01-01 00:00:00'),
('A3LDT7M6J1OZUH', '2020-01-01 00:00:00'),
('A28BFN20WKZJRU', '2020-01-01 00:00:00'),
('A2F3O09R621N7L', '2020-01-01 00:00:00'),
('A2I0XHD58EM6DE', '2020-01-01 00:00:00'),
('A2NL3Y3Y7U50YS', '2020-01-01 00:00:00');
