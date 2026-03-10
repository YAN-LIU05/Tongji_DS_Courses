create database exp1;
use exp1;

CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT NOT NULL,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Phone VARCHAR(20) NOT NULL,
    RegistrationDate DATE NOT NULL DEFAULT (date(current_timestamp)),
    PRIMARY KEY (CustomerID),
    -- 检查邮箱是否包含 @ 和 .
    CHECK (Email LIKE '%@%.%'),
    -- 检查电话（如果非空，长度为 11 且全为数字）
    CHECK (LENGTH(Phone) = 11 AND Phone NOT LIKE '%[^0-9]%')
);

CREATE TABLE Categories (
    CategoryID INT AUTO_INCREMENT NOT NULL,
    CategoryName VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (CategoryID)
);

CREATE TABLE Products (
    ProductID INT AUTO_INCREMENT NOT NULL,
    ProductName VARCHAR(100) NOT NULL,
    Price DECIMAL(10,2) NOT NULL CHECK (Price > 0),
    StockQuantity INT NOT NULL CHECK (StockQuantity >= 0),
    CategoryID INT NOT NULL,
    PRIMARY KEY (ProductID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

CREATE TABLE Orders (
    OrderID INT AUTO_INCREMENT NOT NULL,
    CustomerID INT NOT NULL,
    OrderDate DATETIME NOT NULL DEFAULT current_timestamp,
    TotalAmount DECIMAL(10,2) NOT NULL CHECK (TotalAmount >= 0),
    PRIMARY KEY (OrderID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

CREATE TABLE OrderItems (
    OrderItemID INT AUTO_INCREMENT NOT NULL,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL CHECK (Quantity > 0),
    Subtotal DECIMAL(10,2) NOT NULL CHECK (Subtotal > 0),
    PRIMARY KEY (OrderItemID),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- 触发器：设置OrderItems.Subtotal = Products.Price * OrderItems.Quantity
DELIMITER //
CREATE TRIGGER before_orderitems_insert
BEFORE INSERT ON OrderItems
FOR EACH ROW
BEGIN
    DECLARE product_price DECIMAL(10,2);
    
    -- 获取产品价格
    SELECT Price INTO product_price
    FROM Products
    WHERE ProductID = NEW.ProductID;
    
    -- 设置 Subtotal = Price * Quantity
    SET NEW.Subtotal = product_price * NEW.Quantity;
END //
DELIMITER ;

show tables;

desc Customers;
desc Products;
desc Categories;
desc Orders;
desc OrderItems;

SELECT table_name, constraint_name, constraint_type
FROM information_schema.TABLE_CONSTRAINTS
WHERE table_name = 'Customers';

SELECT table_name, constraint_name, constraint_type
FROM information_schema.TABLE_CONSTRAINTS
WHERE table_name = 'Products';

SELECT table_name, constraint_name, constraint_type
FROM information_schema.TABLE_CONSTRAINTS
WHERE table_name = 'Categories';

SELECT table_name, constraint_name, constraint_type
FROM information_schema.TABLE_CONSTRAINTS
WHERE table_name = 'Orders';

SELECT table_name, constraint_name, constraint_type
FROM information_schema.TABLE_CONSTRAINTS
WHERE table_name = 'OrderItems';

ALTER TABLE Customers
ADD LastLoginDate DATETIME NOT NULL;

DELIMITER //
CREATE TRIGGER before_customers_insert
BEFORE INSERT ON Customers
FOR EACH ROW
BEGIN
    -- 新用户注册时，设置 LastLoginDate 为当前时间
    SET NEW.LastLoginDate = CURRENT_TIMESTAMP;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER before_customers_update
BEFORE UPDATE ON Customers
FOR EACH ROW
BEGIN
    -- 在用户登录（更新）时，自动设置 LastLoginDate 为当前时间
    SET NEW.LastLoginDate = current_timestamp;
END //
DELIMITER ;

UPDATE Customers
SET Name = LEFT(Name, 15)
WHERE LENGTH(Name) > 15;

ALTER TABLE Customers
MODIFY COLUMN Name CHAR(15) NOT NULL;

ALTER TABLE Products
ADD IsFeatured BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX idx_isfeatured ON Products(IsFeatured);

SHOW INDEX FROM Products;

EXPLAIN SELECT * FROM Products WHERE IsFeatured = TRUE;

SELECT ProductID, ProductName, Price
FROM Products
WHERE IsFeatured = TRUE;

DELIMITER //
CREATE PROCEDURE DeleteOrphanedCategories()
BEGIN
    -- 声明变量用于错误处理和记录删除行数
    DECLARE deleted_rows INT DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        -- 错误发生时回滚事务并返回错误信息
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'An error occurred while deleting orphaned categories';
    END;

    -- 开启事务，确保操作原子性
    START TRANSACTION;

    -- 删除没有关联商品的分类
    DELETE FROM Categories
    WHERE NOT EXISTS (
        SELECT 1
        FROM Products
        WHERE Products.CategoryID = Categories.CategoryID
    );

    -- 获取删除的行数
    SET deleted_rows = ROW_COUNT();

    -- 提交事务
    COMMIT;

    -- 返回删除的行数，用于验证
    SELECT CONCAT('Deleted ', deleted_rows, ' orphaned categories') AS Result;
END //
DELIMITER ;

CALL DeleteOrphanedCategories();