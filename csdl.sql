CREATE DATABASE qlcuahangTivi  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; 
 
USE qlcuahangTivi; 
 
CREATE TABLE sanpham( 
    masanpham  INT AUTO_INCREMENT  PRIMARY KEY, 
    tensanpham VARCHAR(100) ,
    hangsanxuat VARCHAR(50), 
    kichthuoc  VARCHAR(10), 
   loai VARCHAR(100),
    gianhap  DECIMAL (12,2), 
    giaban  DECIMAL (12,2), 
    soluongton INT DEFAULT 0,
    tinhtrang ENUM('mới','trung bay',' đã qua sử dụng') DEFAULT 'mới',
    mota TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE khohang ( 
    maphieu INT AUTO_INCREMENT PRIMARY KEY ,
    loaiphieu ENUM('nhập','xuất') NOT NULL,
    ngaylap DATE NOT NULL,
    nhacungcap VARCHAR (225),
    masanpham INT NOT NULL ,
    soluong INT NOT NULL,
    dongia DECIMAL (12,2),
    ghichu TEXT,
    FOREIGN KEY (masanpham) REFERENCES sanpham(masanpham)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE hoadon (
  mahoadon INT AUTO_INCREMENT PRIMARY KEY,
  ngayban DATE NOT NULL,
  tenkhachhang VARCHAR(255),
  tongtien DECIMAL(14,2),
  nhanvienbanhang VARCHAR(255),
  hinhthuctt ENUM('tiền mặt','chuyển khoản','trả góp','quẹt thẻ'),
  ghichu TEXT

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE chitiethoadon (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mahoadon INT,
  masanpham INT,
  tensanpham VARCHAR(255),
  soluong INT,
  dongia DECIMAL(12,2),
  thanhtien DECIMAL(14,2) AS (soluong * dongia) STORED,
  FOREIGN KEY (mahoadon) REFERENCES hoadon(mahoadon),
  FOREIGN KEY (masanpham) REFERENCES sanpham(masanpham)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
DROP TABLE IF EXISTS chitiethoadon;
CREATE TABLE khachhang (
  makhachhang INT AUTO_INCREMENT PRIMARY KEY,
  hoten VARCHAR(255) NOT NULL,
  sodienthoai VARCHAR(20),
  diachi VARCHAR(255),
  lichsumuahang TEXT,
  chinhsach VARCHAR(255)           -- bảo hành/đổi trả đã áp dụng
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE nhanvien (
  manhanvien INT AUTO_INCREMENT PRIMARY KEY,
  hoten VARCHAR(255) NOT NULL,
  vitri VARCHAR(100),
  luong DECIMAL(12,2),
  thuong DECIMAL(12,2),
  calam VARCHAR(50),
  hieusuat DECIMAL(5,2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DELIMITER $$

CREATE TRIGGER tgcapnhattonkho
AFTER INSERT ON khohang
FOR EACH ROW
BEGIN
  IF NEW.loaiphieu = 'nhập' THEN
    UPDATE sanpham 
    SET soluongton = soluongton + NEW.soluong
    WHERE masanpham = NEW.masanpham;
  ELSEIF NEW.loaiphieu = 'xuất' THEN
    UPDATE sanpham 
    SET soluongton = soluongton - NEW.soluong
    WHERE masanpham = NEW.masanpham;
  END IF;
END$$
DELIMITER ;
-- Sản phẩm
INSERT INTO sanpham (tensanpham, hangsanxuat, kichthuoc, loai, gianhap, giaban, soluongton, tinhtrang, mota)
VALUES
('Sony Bravia 55X', 'Sony', 55, 'Smart TV 4K', 12000000, 1, 10, 'mới', 'Màn hình 55 inch, độ phân giải 4K'),
('Samsung QLED 65Q', 'Samsung', 65, 'QLED 4K', 20000000, 2, 5, 'mới', 'TV QLED 65 inch 4K siêu mỏng');

-- Nhập kho
INSERT INTO khohang (loaiphieu, ngaylap, nhacungcap, masanpham, soluong, dongia)
VALUES ('nhập', '2025-10-21', 'Công ty Samsung ', 1, 5, 12000000);

-- Hóa đơn bán
INSERT INTO hoadon (ngayban, tenkhachhang, tongtien, nhanvienbanhang, hinhthuctt, ghichu)
VALUES ('2025-10-21', 'Nguyễn Văn An  ', 36000000, 'Trần Thị Bảo Hân ', 'tiền mặt', 'Giảm giá 5%');

-- Chi tiết hóa đơn
INSERT INTO chitiethoadon (mahoadon, masanpham, tensanpham, soluong, dongia)
VALUES (1, 1, 'Sony Bravia 55X', 2, 18000000);
SELECT masanpham, tensanpham, hangsanxuat, soluongton
FROM sanpham;
SELECT nhanvienbanhang, SUM(tongtien) AS tongdoanhso
FROM hoadon
GROUP BY nhanvienbanhang;
SELECT h.mahoadon, h.ngayban, c.tensanpham, c.soluong, c.dongia
FROM hoadon h
JOIN chitiethoadon c ON h.mahoadon = c.mahoadon
WHERE h.tenkhachhang = 'Nguyễn Văn An ';
SELECT * FROM sanpham;
SELECT * FROM khachhang;
SELECT * FROM nhanvien;




    