"""
ql_tivi_app.py
Ứng dụng GUI quản lý cửa hàng Tivi (Tkinter + MySQL)
Hỗ trợ: sản phẩm, kho, hóa đơn + chi tiết, khách hàng
Yêu cầu: pip install mysql-connector-python
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

# ---------------------------
# Cấu hình DB - chỉnh ở đây
# ---------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "15082005",        
    "database": "qlcuahangTivi"
}

# ---------------------------
# Hàm kết nối
# ---------------------------
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Lỗi kết nối MySQL", str(e))
        return None

# ---------------------------
# UTIL: Hiển thị lỗi / commit
# ---------------------------
def db_commit(conn):
    try:
        conn.commit()
    except Exception as e:
        messagebox.showerror("Lỗi commit", str(e))


# ---------------------------
# QUAN LI SAN PHAM
# ---------------------------
def open_product_manager():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    win = tk.Tk()
    win.title("Quản lý sản phẩm Tivi")
    win.geometry("1100x650")

    cols = ("masanpham", "tensanpham", "hangsanxuat", "kichthuoc", "loai", 
            "gianhap", "giaban", "soluongton", "tinhtrang", "mota")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=100, anchor="center")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    

    # --- Form nhập ---
    frm = tk.Frame(win)
    frm.pack(padx=10, pady=5, fill="x")

    labels = ["Tên sản phẩm", "Hãng SX", "Kích thước", "Loại", 
              "Giá nhập", "Giá bán", "Số lượng", "Tình trạng", "Mô tả"]
    entries = {}
    for i, lbl in enumerate(labels):
        tk.Label(frm, text=lbl).grid(row=i//3, column=(i%3)*2, sticky="e", padx=5, pady=5)
        if lbl == "Mô tả":
            entries[lbl] = tk.Text(frm, height=3, width=40)
            entries[lbl].grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5)
        elif lbl == "Tình trạng":
            var = tk.StringVar(value="Mới")
            cb = ttk.Combobox(frm, textvariable=var, values=["Mới","Trưng bày","Đã qua sử dụng"])
            cb.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5)
            entries[lbl] = var
        else:
            e = tk.Entry(frm)
            e.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5)
            entries[lbl] = e

    # --- Biến trạng thái ---
    edit_mode = {"status": None, "id": None}

    # --- Load dữ liệu ---
    def load_products():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM sanpham")
        for r in cursor.fetchall():
            tree.insert("", tk.END, values=r)

    # --- Làm sạch form ---
    def clear_form():
        for e in entries.values():
            e.delete(0, tk.END)
        edit_mode["status"] = None
        edit_mode["id"] = None

    # --- Khi chọn dòng ---
    def on_select(ev):
        sel = tree.focus()
        if not sel:
            return
        v = tree.item(sel)["values"]
        edit_mode["id"] = v[0]
        entries["Tên sản phẩm"].delete(0, tk.END); entries["Tên sản phẩm"].insert(0, v[1])
        entries["Hãng SX"].delete(0, tk.END); entries["Hãng SX"].insert(0, v[2])
        entries["Kích thước"].delete(0, tk.END); entries["Kích thước"].insert(0, v[3])
        entries["Loại"].delete(0, tk.END); entries["Loại"].insert(0, v[4])
        entries["Giá nhập"].delete(0, tk.END); entries["Giá nhập"].insert(0, v[5])
        entries["Giá bán"].delete(0, tk.END); entries["Giá bán"].insert(0, v[6])
        entries["Số lượng"].delete(0, tk.END); entries["Số lượng"].insert(0, v[7])
        entries["Tình trạng"].delete(0, tk.END); entries["Tình trạng"].insert(0, v[8])
        entries["Mô tả"].delete(0, tk.END); entries["Mô tả"].insert(0, v[9])

    # --- Thêm mới ---
    def add_product():
        clear_form()
        edit_mode["status"] = "add"
        messagebox.showinfo("Thêm sản phẩm", "Nhập thông tin và bấm Lưu để thêm mới.")

    # --- Lưu (thêm hoặc sửa) ---
    def save_product():
        data = (
            entries["Tên sản phẩm"].get(),
            entries["Hãng SX"].get(),
            entries["Kích thước"].get(),
            entries["Loại"].get(),
            float(entries["Giá nhập"].get() or 0),
            float(entries["Giá bán"].get() or 0),
            int(entries["Số lượng"].get() or 0),
            entries["Tình trạng"].get() or "mới",
            entries["Mô tả"].get()
        )

        try:
            if edit_mode["status"] == "add":
                cursor.execute("""
                    INSERT INTO sanpham (tensanpham, hangsanxuat, kichthuoc, loai, 
                                         gianhap, giaban, soluongton, tinhtrang, mota)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, data)
                db_commit(conn)
                messagebox.showinfo("Thành công", "Đã thêm sản phẩm mới.")
            elif edit_mode["status"] == "edit" and edit_mode["id"]:
                cursor.execute("""
                    UPDATE sanpham SET tensanpham=%s, hangsanxuat=%s, kichthuoc=%s, loai=%s, 
                        gianhap=%s, giaban=%s, soluongton=%s, tinhtrang=%s, mota=%s
                    WHERE masanpham=%s
                """, data + (edit_mode["id"],))
                db_commit(conn)
                messagebox.showinfo("Thành công", "Đã cập nhật sản phẩm.")
            else:
                messagebox.showwarning("Chú ý", "Vui lòng chọn Thêm hoặc Sửa trước khi Lưu.")
            load_products()
            clear_form()
        except Exception as e:
            messagebox.showerror("Lỗi lưu", str(e))

    # --- Sửa ---
    def edit_product():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Vui lòng chọn sản phẩm cần sửa.")
            return
        edit_mode["status"] = "edit"
        messagebox.showinfo("Chế độ sửa", "Bạn có thể chỉnh thông tin và bấm Lưu.")

    # --- Hủy ---
    def cancel_edit():
        clear_form()
        messagebox.showinfo("Hủy", "Đã hủy thao tác.")

    # --- Xóa ---
    def delete_product():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Vui lòng chọn sản phẩm cần xóa.")
            return
        v = tree.item(sel)["values"]
        if messagebox.askyesno("Xác nhận", f"Bạn chắc muốn xóa sản phẩm '{v[1]}'?"):
            cursor.execute("DELETE FROM sanpham WHERE masanpham=%s", (v[0],))
            db_commit(conn)
            load_products()
            clear_form()
            messagebox.showinfo("Đã xóa", "Sản phẩm đã bị xóa.")
    # --- Thanh tìm kiếm ---
    search_frame = tk.Frame(win)
    search_frame.pack(pady=5)
    tk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(search_frame, width=40)
    search_entry.pack(side=tk.LEFT, padx=5)
    def search_product():
        key = search_entry.get().strip()
        if not key:
            messagebox.showwarning("Tìm kiếm", "Vui lòng nhập từ khóa.")
            return
        tree.delete(*tree.get_children())
        cursor.execute("""
            SELECT * FROM sanpham 
            WHERE tensanpham LIKE %s OR hangsanxuat LIKE %s
        """, (f"%{key}%", f"%{key}%"))
        for r in cursor.fetchall():
            tree.insert("", tk.END, values=r)

    def show_all():
        search_entry.delete(0, tk.END)
        load_products()

    tk.Button(search_frame, text="Tìm", command=search_product).pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Hiển thị tất cả", command=show_all).pack(side=tk.LEFT, padx=5)


    # --- Thoát ---
    def exit_window():
        cursor.close()
        conn.close()
        win.destroy()

    # --- Nút chức năng ---
    btnf = tk.Frame(win)
    btnf.pack(pady=10)
    tk.Button(btnf, text="Thêm", width=12, command=add_product).grid(row=0, column=0, padx=5)
    tk.Button(btnf, text="Lưu", width=12, command=save_product).grid(row=0, column=1, padx=5)
    tk.Button(btnf, text="Sửa", width=12, command=edit_product).grid(row=0, column=2, padx=5)
    tk.Button(btnf, text="Hủy", width=12, command=cancel_edit).grid(row=0, column=3, padx=5)
    tk.Button(btnf, text="Xóa", width=12, command=delete_product).grid(row=0, column=4, padx=5)
    tk.Button(btnf, text="Thoát", width=12, command=exit_window).grid(row=0, column=5, padx=5)

    tree.bind("<<TreeviewSelect>>", on_select)
    load_products()
    win.mainloop()
 


# ---------------------------
# QUAN LI KHO HANG
# ---------------------------

def open_stock_manager():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    win = tk.Tk()
    win.title("Quản lý kho hàng")
    win.geometry("950x600")

    window_width = 900
    window_height = 600

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))

    win.geometry(f"{window_width}x{window_height}+{x}+{y}")

    cols = ("maphieu","loaiphieu","ngaylap","nhacungcap","masanpham","soluong","dongia","ghichu","thanhtien")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=110, anchor="center")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    


    # --- Form nhập ---
    frm = tk.Frame(win); frm.pack(padx=10, pady=5, fill="x")
    tk.Label(frm, text="Loại phiếu").grid(row=0, column=0)
    loaivar = tk.StringVar(value="Nhập")
    cb_loai = ttk.Combobox(frm, textvariable=loaivar, values=["Nhập","Xuất"], width=15)
    cb_loai.grid(row=0, column=1)

    tk.Label(frm, text="Ngày (YYYY-MM-DD)").grid(row=0, column=2)
    ngay_entry = tk.Entry(frm, width=20); ngay_entry.grid(row=0, column=3)
    ngay_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    tk.Label(frm, text="Nhà cung cấp").grid(row=1, column=0)
    nhacungcap_entry = tk.Entry(frm, width=25); nhacungcap_entry.grid(row=1, column=1)

    tk.Label(frm, text="Mã sản phẩm").grid(row=1, column=2)
    masp_entry = tk.Entry(frm, width=20); masp_entry.grid(row=1, column=3)

    tk.Label(frm, text="Số lượng").grid(row=2, column=0)
    soluong_entry = tk.Entry(frm, width=20); soluong_entry.grid(row=2, column=1)

    tk.Label(frm, text="Đơn giá").grid(row=2, column=2)
    dongia_entry = tk.Entry(frm, width=20); dongia_entry.grid(row=2, column=3)

    tk.Label(frm, text="Ghi chú").grid(row=3, column=0)
    ghichu_entry = tk.Entry(frm, width=70); ghichu_entry.grid(row=3, column=1, columnspan=3, pady=5)

    tk.Label(frm, text="Thành tiền").grid(row=4, column=0)
    thanhtien_entry = tk.Entry(frm, width=70); thanhtien_entry.grid(row=4, column=1, columnspan=3, pady=5)

    # Biến trạng thái
    edit_mode = {"status": None, "id": None}

    # --- Load dữ liệu ---
    def load_stock():
        tree.delete(*tree.get_children())
        try:
            cursor.execute("SELECT maphieu, loaiphieu, ngaylap, nhacungcap, masanpham, soluong, dongia, ghichu FROM khohang")
            for r in cursor.fetchall():
                thanhtien = r[5] * r[6]  # soluong * dongia
                tree.insert("", tk.END, values=r + (thanhtien,))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # --- Làm sạch form ---
    def clear_form():
        loaivar.set("Nhập")
        ngay_entry.delete(0, tk.END); ngay_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        nhacungcap_entry.delete(0, tk.END)
        masp_entry.delete(0, tk.END)
        soluong_entry.delete(0, tk.END)
        dongia_entry.delete(0, tk.END)
        ghichu_entry.delete(0, tk.END)
        edit_mode["status"] = None
        edit_mode["id"] = None

    # --- Khi chọn dòng ---
    def on_select(ev):
        sel = tree.focus()
        if not sel: return
        v = tree.item(sel)["values"]
        edit_mode["id"] = v[0]
        loaivar.set(v[1])
        ngay_entry.delete(0, tk.END); ngay_entry.insert(0, v[2])
        nhacungcap_entry.delete(0, tk.END); nhacungcap_entry.insert(0, v[3])
        masp_entry.delete(0, tk.END); masp_entry.insert(0, v[4])
        soluong_entry.delete(0, tk.END); soluong_entry.insert(0, v[5])
        dongia_entry.delete(0, tk.END); dongia_entry.insert(0, v[6])
        ghichu_entry.delete(0, tk.END); ghichu_entry.insert(0, v[7])
        thanhtien_entry.delete(0, tk.END); thanhtien_entry.insert(0, v[8])

    # --- Thêm phiếu ---
    def add_phieu():
        try:
            sql = """INSERT INTO khohang (loaiphieu, ngaylap, nhacungcap, masanpham, soluong, dongia, ghichu)
                     VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            vals = (
                loaivar.get(),
                ngay_entry.get(),
                nhacungcap_entry.get(),
                int(masp_entry.get()),
                int(soluong_entry.get()),
                float(dongia_entry.get() or 0),
                ghichu_entry.get(),
                thanhtien_entry.get()
            )
            cursor.execute(sql, vals)
            db_commit(conn)
            load_stock()
            clear_form()
            messagebox.showinfo("Thành công", "Đã ghi nhận phiếu mới.")
        except Exception as e:
            messagebox.showerror("Lỗi thêm phiếu", str(e))

    # --- Sửa phiếu ---
    def edit_phieu():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Vui lòng chọn phiếu cần sửa.")
            return
        edit_mode["status"] = "edit"
        messagebox.showinfo("Chế độ sửa", "Hãy chỉnh thông tin và bấm 'Lưu thay đổi'.")

    # --- Lưu thay đổi ---
    def save_edit():
        if edit_mode["status"] != "edit" or not edit_mode["id"]:
            messagebox.showwarning("Chú ý", "Bạn cần chọn phiếu và bấm 'Sửa' trước.")
            return
        try:
            sql = """UPDATE khohang SET loaiphieu=%s, ngaylap=%s, nhacungcap=%s, masanpham=%s,
                     soluong=%s, dongia=%s, ghichu=%s WHERE maphieu=%s"""
            vals = (
                loaivar.get(),
                ngay_entry.get(),
                nhacungcap_entry.get(),
                int(masp_entry.get()),
                int(soluong_entry.get()),
                float(dongia_entry.get() or 0),
                ghichu_entry.get(),
                edit_mode["id"]
                
            )
            cursor.execute(sql, vals)
            db_commit(conn)
            load_stock()
            clear_form()
            messagebox.showinfo("Thành công", "Đã cập nhật phiếu kho.")
        except Exception as e:
            messagebox.showerror("Lỗi lưu", str(e))

    # --- Xóa phiếu ---
    def delete_phieu():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn dòng", "Chọn phiếu để xóa.")
            return
        item = tree.item(sel)
        maphieu = item['values'][0]
        if not messagebox.askyesno("Xác nhận", f"Xóa phiếu {maphieu}?"):
            return
        try:
            cursor.execute("DELETE FROM khohang WHERE maphieu=%s", (maphieu,))
            db_commit(conn)
            load_stock()
            clear_form()
            messagebox.showinfo("Đã xóa", "Xóa thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi xóa", str(e))

    # --- Nút chức năng ---
    btnf = tk.Frame(win); btnf.pack(pady=10)
    tk.Button(btnf, text="Thêm phiếu", command=add_phieu, width=14).grid(row=0, column=0, padx=5)
    tk.Button(btnf, text="Sửa phiếu", command=edit_phieu, width=14).grid(row=0, column=1, padx=5)
    tk.Button(btnf, text="Lưu thay đổi", command=save_edit, width=14).grid(row=0, column=2, padx=5)
    tk.Button(btnf, text="Xóa phiếu", command=delete_phieu, width=14).grid(row=0, column=3, padx=5)
    tk.Button(btnf, text="Tải lại", command=load_stock, width=14).grid(row=0, column=4, padx=5)
    tk.Button(btnf, text="Đóng", command=lambda:[cursor.close(), conn.close(), win.destroy()], width=14).grid(row=0, column=5, padx=5)

    tree.bind("<<TreeviewSelect>>", on_select)
    load_stock()
    win.mainloop()

    btnf = tk.Frame(win); btnf.pack(pady=8)
    tk.Button(btnf, text="Ghi nhận phiếu", command=add_phieu, width=15).grid(row=0, column=0, padx=5)
    tk.Button(btnf, text="Xóa phiếu", command=delete_phieu, width=15).grid(row=0, column=1, padx=5)
    tk.Button(btnf, text="Sửa", width=12, command=edit_phieu).grid(row=0, column=2, padx=5)

    tk.Button(btnf, text="Đóng", command=lambda:[cursor.close(), conn.close(), win.destroy()], width=15).grid(row=0, column=3, padx=5)

    load_stock()
    win.mainloop()


# ---------------------------
# QUAN LI KHACH HANG
# ---------------------------
def open_customer_manager():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    win = tk.Tk()
    win.title("Quản lý khách hàng")
    win.geometry("900x600")

    cols = ("makhachhang","hoten","sodienthoai","diachi","lichsumuahang","chinhsach")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=130)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frm = tk.Frame(win); frm.pack(padx=10, pady=5, fill="x")
    tk.Label(frm, text="Họ tên").grid(row=0, column=0)
    hoten_entry = tk.Entry(frm); hoten_entry.grid(row=0, column=1)
    tk.Label(frm, text="SĐT").grid(row=0, column=2)
    sdt_entry = tk.Entry(frm); sdt_entry.grid(row=0, column=3)
    tk.Label(frm, text="Địa chỉ").grid(row=1, column=0)
    diachi_entry = tk.Entry(frm); diachi_entry.grid(row=1, column=1)
    tk.Label(frm, text="Lịch sử mua").grid(row=1, column=2)
    lichsu_entry = tk.Entry(frm); lichsu_entry.grid(row=1, column=3)
    tk.Label(frm, text="Chính sách").grid(row=2, column=0)
    chinhsach_entry = tk.Entry(frm); chinhsach_entry.grid(row=2, column=1)

    def load_customers():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT makhachhang,hoten,sodienthoai,diachi,lichsumuahang,chinhsach FROM khachhang")
        for r in cursor.fetchall():
            tree.insert("", tk.END, values=r)

    def add_customer():
        try:
            sql = """INSERT INTO khachhang (hoten, sodienthoai, diachi, lichsumuahang, chinhsach)
                     VALUES (%s,%s,%s,%s,%s)"""
            vals = (
                hoten_entry.get(),
                sdt_entry.get(),
                diachi_entry.get(),
                lichsu_entry.get(),
                chinhsach_entry.get()
            )
            cursor.execute(sql, vals)
            db_commit(conn)
            load_customers()
            messagebox.showinfo("Thành công", "Đã thêm khách hàng.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def update_customer():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Chọn khách hàng để sửa.")
            return
        makh = tree.item(sel)["values"][0]
        try:
            sql = """UPDATE khachhang SET hoten=%s, sodienthoai=%s, diachi=%s, lichsumuahang=%s, chinhsach=%s
                     WHERE makhachhang=%s"""
            vals = (
                hoten_entry.get(), sdt_entry.get(), diachi_entry.get(), lichsu_entry.get(), chinhsach_entry.get(), makh
            )
            cursor.execute(sql, vals)
            db_commit(conn)
            load_customers()
            messagebox.showinfo("Thành công", "Đã cập nhật.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def delete_customer():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Chọn khách hàng để xóa.")
            return
        makh = tree.item(sel)["values"][0]
        if not messagebox.askyesno("Xác nhận", f"Xóa khách hàng {makh}?"):
            return
        try:
            cursor.execute("DELETE FROM khachhang WHERE makhachhang=%s", (makh,))
            db_commit(conn)
            load_customers()
            messagebox.showinfo("Đã xóa", "Xóa thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    def save_customer():
        sel = tree.focus()
        try:
            if sel:  # có chọn => cập nhật
                makh = tree.item(sel)["values"][0]
                sql = """UPDATE khachhang 
                        SET hoten=%s, sodienthoai=%s, diachi=%s, lichsumuahang=%s, chinhsach=%s
                        WHERE makhachhang=%s"""
                vals = (
                    hoten_entry.get(), 
                    sdt_entry.get(), 
                    diachi_entry.get(), 
                    lichsu_entry.get(), 
                    chinhsach_entry.get(), 
                    makh
                )
                cursor.execute(sql, vals)
                db_commit(conn)
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin khách hàng.")
            else:  # chưa chọn => thêm mới
                sql = """INSERT INTO khachhang (hoten, sodienthoai, diachi, lichsumuahang, chinhsach)
                        VALUES (%s, %s, %s, %s, %s)"""
                vals = (
                    hoten_entry.get(),
                    sdt_entry.get(),
                    diachi_entry.get(),
                    lichsu_entry.get(),
                    chinhsach_entry.get()
                )
                cursor.execute(sql, vals)
                db_commit(conn)
                messagebox.showinfo("Thành công", "Đã lưu khách hàng mới.")
            load_customers()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


    def on_select(ev):
        sel = tree.focus()
        if not sel: return
        v = tree.item(sel)["values"]
        hoten_entry.delete(0, tk.END); hoten_entry.insert(0, v[1])
        sdt_entry.delete(0, tk.END); sdt_entry.insert(0, v[2])
        diachi_entry.delete(0, tk.END); diachi_entry.insert(0, v[3])
        lichsu_entry.delete(0, tk.END); lichsu_entry.insert(0, v[4] if v[4] else "")
        chinhsach_entry.delete(0, tk.END); chinhsach_entry.insert(0, v[5] if v[5] else "")

    btnf = tk.Frame(win); btnf.pack(pady=8)
    tk.Button(btnf, text="Thêm", command=add_customer, width=12).grid(row=0, column=0, padx=5)
    tk.Button(btnf, text="Cập nhật", command=update_customer, width=12).grid(row=0, column=1, padx=5)
    tk.Button(btnf, text="Lưu", command=save_customer, width=12).grid(row=0, column=2, padx=5)
    tk.Button(btnf, text="Xóa", command=delete_customer, width=12).grid(row=0, column=3, padx=5)
    tk.Button(btnf, text="Đóng", command=lambda:[cursor.close(), conn.close(), win.destroy()], width=12).grid(row=0, column=4, padx=5)
   

    tree.bind("<<TreeviewSelect>>", on_select)
    load_customers()
    win.mainloop()


# ---------------------------
# QUAN LI HOA DON (hoadon + chitiethoadon)
# ---------------------------

def open_invoice_manager():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    win = tk.Tk()
    win.title("📄 Quản lý Hóa đơn Bán Hàng")
    win.geometry("1150x750")
    win.configure(bg="#f4f6f8")
    

    # ---- FRAME DANH SÁCH HÓA ĐƠN ----
    frm_hd = tk.LabelFrame(win, text="Danh sách hóa đơn", bg="#f4f6f8", fg="#333", font=("Arial", 11, "bold"))
    frm_hd.pack(fill="both", expand=False, padx=10, pady=8)

    cols_hd = ("mahoadon", "ngayban", "tenkhachhang", "tongtien", "nhanvienbanhang", "hinhthuctt", "ghichu")
    tree_hd = ttk.Treeview(frm_hd, columns=cols_hd, show="headings", height=5)
    for c in cols_hd:
        tree_hd.heading(c, text=c.title())
        tree_hd.column(c, width=150)
    tree_hd.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    # ---- FRAME CHI TIẾT ----
    frm_ct = tk.LabelFrame(win, text="Chi tiết hóa đơn", bg="#f4f6f8", fg="#333", font=("Arial", 11, "bold"))
    frm_ct.pack(fill="both", expand=True, padx=10, pady=8)

    cols_ct = ("id","mahoadon", "masanpham", "tensanpham", "soluong", "dongia", "thanhtien")
    tree_ct = ttk.Treeview(frm_ct, columns=cols_ct, show="headings",height=5)
    for c in cols_ct:
        tree_ct.heading(c, text=c.title())
        tree_ct.column(c, width=120)
    tree_ct.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    # ---- FORM HÓA ĐƠN ----
    frm = tk.LabelFrame(win, text="Thông tin hóa đơn", bg="#f4f6f8", fg="#333", font=("Arial", 11, "bold"))
    frm.pack(fill="x", padx=10, pady=5)

    tk.Label(frm, text="Ngày (YYYY-MM-DD):", bg="#f4f6f8").grid(row=0, column=0, sticky="e", pady=3)
    ngay_entry = tk.Entry(frm, width=20)
    ngay_entry.grid(row=0, column=1, padx=5, pady=3)
    ngay_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    tk.Label(frm, text="Khách hàng:", bg="#f4f6f8").grid(row=0, column=2, sticky="e", pady=3)
    tenkh_entry = tk.Entry(frm, width=25)
    tenkh_entry.grid(row=0, column=3, padx=5, pady=3)

    tk.Label(frm, text="Nhân viên bán:", bg="#f4f6f8").grid(row=1, column=0, sticky="e", pady=3)
    nv_entry = tk.Entry(frm, width=20)
    nv_entry.grid(row=1, column=1, padx=5, pady=3)

    tk.Label(frm, text="Hình thức TT:", bg="#f4f6f8").grid(row=1, column=2, sticky="e", pady=3)
    hinhthuc_var = tk.StringVar(value="tiền mặt")
    ttk.Combobox(frm, textvariable=hinhthuc_var, values=["tiền mặt", "chuyển khoản", "trả góp", "quẹt thẻ"], width=22).grid(row=1, column=3, padx=5, pady=3)

    tk.Label(frm, text="Ghi chú:", bg="#f4f6f8").grid(row=2, column=0, sticky="e", pady=3)
    ghichu_entry = tk.Entry(frm, width=60)
    ghichu_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=3)

    # ---- FORM CHI TIẾT ----
    frm2 = tk.LabelFrame(win, text="Thêm sản phẩm vào hóa đơn", bg="#f4f6f8", fg="#333", font=("Arial", 11, "bold"))
    frm2.pack(fill="x", padx=10, pady=5)

    tk.Label(frm2, text="Mã hóa đơn:", bg="#f4f6f8").grid(row=0, column=0)
    mahoadon_entry = tk.Entry(frm2, width=10); mahoadon_entry.grid(row=0, column=1, padx=5)

    tk.Label(frm2, text="Mã SP:", bg="#f4f6f8").grid(row=0, column=2)
    masp_entry = tk.Entry(frm2, width=10); masp_entry.grid(row=0, column=3, padx=5)

    tk.Label(frm2, text="Tên SP:", bg="#f4f6f8").grid(row=1, column=0)
    tensp_entry = tk.Entry(frm2, width=20); tensp_entry.grid(row=1, column=1, padx=5)

    tk.Label(frm2, text="Số lượng:", bg="#f4f6f8").grid(row=1, column=2)
    soluong_entry = tk.Entry(frm2, width=10); soluong_entry.grid(row=1, column=3, padx=5)

    tk.Label(frm2, text="Đơn giá:", bg="#f4f6f8").grid(row=2, column=0)
    dongia_entry = tk.Entry(frm2, width=10); dongia_entry.grid(row=2, column=1, padx=5)

    # ---- HÀM XỬ LÝ ----
    def load_invoices():
        tree_hd.delete(*tree_hd.get_children())
        cursor.execute("SELECT mahoadon, ngayban, tenkhachhang, tongtien, nhanvienbanhang, hinhthuctt, ghichu FROM hoadon")
        for r in cursor.fetchall():
            tree_hd.insert("", tk.END, values=r)

    def load_invoice_details(mahd):
        tree_ct.delete(*tree_ct.get_children())
        cursor.execute("SELECT id, mahoadon, masanpham, tensanpham, soluong, dongia, thanhtien FROM chitiethoadon WHERE mahoadon=%s", (mahd,))
        for r in cursor.fetchall():
            tree_ct.insert("", tk.END, values=r)

    def create_invoice():
        try:
            sql = """INSERT INTO hoadon (ngayban, tenkhachhang, tongtien, nhanvienbanhang, hinhthuctt, ghichu)
                     VALUES (%s,%s,%s,%s,%s,%s)"""
            vals = (ngay_entry.get(), tenkh_entry.get(), 0.0, nv_entry.get(), hinhthuc_var.get(), ghichu_entry.get())
            cursor.execute(sql, vals)
            db_commit(conn)
            load_invoices()
            messagebox.showinfo("Thành công", "Đã tạo hóa đơn mới.")
        except Exception as e:
            messagebox.showerror("Lỗi tạo hóa đơn", str(e))

    def edit_invoice():
        sel = tree_hd.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Chọn hóa đơn để sửa.")
            return
        mahd = tree_hd.item(sel)["values"][0]
        try:
            sql = """UPDATE hoadon SET ngayban=%s, tenkhachhang=%s, nhanvienbanhang=%s, hinhthuctt=%s, ghichu=%s WHERE mahoadon=%s"""
            vals = (ngay_entry.get(), tenkh_entry.get(), nv_entry.get(), hinhthuc_var.get(), ghichu_entry.get(), mahd)
            cursor.execute(sql, vals)
            db_commit(conn)
            load_invoices()
            messagebox.showinfo("Thành công", "Đã cập nhật hóa đơn.")
        except Exception as e:
            messagebox.showerror("Lỗi sửa hóa đơn", str(e))

    def add_invoice_item():
        try:
            mahd = int(mahoadon_entry.get())
            masp = int(masp_entry.get())
            tensp = tensp_entry.get()
            sl = int(soluong_entry.get())
            dg = float(dongia_entry.get())

            sql = """INSERT INTO chitiethoadon (mahoadon, masanpham, tensanpham, soluong, dongia)
                     VALUES (%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (mahd, masp, tensp, sl, dg))
            db_commit(conn)

            cursor.execute("SELECT SUM(soluong * dongia) FROM chitiethoadon WHERE mahoadon=%s", (mahd,))
            tong = cursor.fetchone()[0] or 0
            cursor.execute("UPDATE hoadon SET tongtien=%s WHERE mahoadon=%s", (tong, mahd))
            db_commit(conn)

            load_invoice_details(mahd)
            load_invoices()
            messagebox.showinfo("Thành công", "Đã thêm sản phẩm vào hóa đơn.")
        except Exception as e:
            messagebox.showerror("Lỗi thêm chi tiết", str(e))

    def delete_invoice():
        sel = tree_hd.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Chọn hóa đơn để xóa.")
            return
        mahd = tree_hd.item(sel)["values"][0]
        if not messagebox.askyesno("Xác nhận", f"Xóa hóa đơn {mahd}?"):
            return
        try:
            cursor.execute("DELETE FROM chitiethoadon WHERE mahoadon=%s", (mahd,))
            cursor.execute("DELETE FROM hoadon WHERE mahoadon=%s", (mahd,))
            db_commit(conn)
            load_invoices()
            tree_ct.delete(*tree_ct.get_children())
            messagebox.showinfo("Đã xóa", "Xóa hóa đơn thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi xóa", str(e))

    def on_invoice_select(ev):
        sel = tree_hd.focus()
        if not sel:
            return
        vals = tree_hd.item(sel)["values"]
        mahd = vals[0]
        mahoadon_entry.delete(0, tk.END)
        mahoadon_entry.insert(0, mahd)
        ngay_entry.delete(0, tk.END)
        ngay_entry.insert(0, vals[1])
        tenkh_entry.delete(0, tk.END)
        tenkh_entry.insert(0, vals[2])
        nv_entry.delete(0, tk.END)
        nv_entry.insert(0, vals[4])
        hinhthuc_var.set(vals[5])
        ghichu_entry.delete(0, tk.END)
        ghichu_entry.insert(0, vals[6])
        load_invoice_details(mahd)
    def save_invoice():
        """Lưu thông tin hóa đơn hiện đang nhập (nếu có mã hóa đơn)."""
        try:
            mahd = mahoadon_entry.get().strip()
            if not mahd:
                messagebox.showwarning("Thiếu mã", "Chưa có mã hóa đơn để lưu.")
                return

            sql = """UPDATE hoadon 
                     SET ngayban=%s, tenkhachhang=%s, nhanvienbanhang=%s, 
                         hinhthuctt=%s, ghichu=%s 
                     WHERE mahoadon=%s"""
            vals = (ngay_entry.get(), tenkh_entry.get(), nv_entry.get(),
                    hinhthuc_var.get(), ghichu_entry.get(), mahd)
            cursor.execute(sql, vals)
            db_commit(conn)
            load_invoices()
            messagebox.showinfo("Thành công", f"Đã lưu thay đổi cho hóa đơn {mahd}.")
        except Exception as e:
            messagebox.showerror("Lỗi lưu", str(e))
            


    # ---- NÚT CHỨC NĂNG ----
    btnf = tk.Frame(win, bg="#f4f6f8")
    btnf.pack(side="bottom",fill="x", padx=10, pady=10)

    style_btn = {"width": 14, "bg":"#4caf50", "fg": "white", "font": ("Arial", 10, "bold")}

# NUT CHUC NANG
    tk.Button(btnf, text="Tạo hóa đơn", command=create_invoice, width=14).grid(row=0, column=0, padx=6, pady=6)
    tk.Button(btnf, text="Sửa hóa đơn", command=edit_invoice, width=14 ).grid(row=0, column=1, padx=6, pady=6)
    tk.Button(btnf, text="Thêm chi tiết", command=add_invoice_item, width=14).grid(row=0, column=2, padx=6, pady=6)
    tk.Button(btnf, text="Xóa hóa đơn", command=delete_invoice,  width=14).grid(row=0, column=3, padx=6, pady=6)
    tk.Button(btnf, text="Tải lại", command=load_invoices, width=14).grid(row=0, column=4, padx=6, pady=6)
    tk.Button(btnf, text="Đóng", command=lambda: [cursor.close(), conn.close(), win.destroy()],
             width=14).grid(row=0, column=5, padx=6, pady=6)
    tk.Button(btnf, text="Lưu", command=save_invoice, width=14).grid(row=0, column=4, padx=6, pady=6)


    for i in range(6):
     btnf.grid_columnconfigure(i, weight=1)
    
    win.geometry("1350x750")

    tree_hd.bind("<<TreeviewSelect>>", on_invoice_select)

    load_invoices()
    win.mainloop()

# ---------------------------
# QUAN LI NHAN VIEN
# ---------------------------
def open_employee_manager():
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()

    win = tk.Tk()
    win.title("Quản lý nhân viên")
    win.geometry("950x600")

    cols = ("manhanvien", "hoten", "vitri", "luong", "thuong", "calam", "hieusuat")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120, anchor="center")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Form nhập ---
    frm = tk.Frame(win)
    frm.pack(padx=10, pady=5, fill="x")

    labels = ["Họ tên", "Vị trí", "Lương", "Thưởng", "Ca làm", "Hiệu suất"]
    entries = {}
    for i, lbl in enumerate(labels):
        tk.Label(frm, text=lbl).grid(row=i // 3, column=(i % 3) * 2, sticky="e", padx=5, pady=5)
        e = tk.Entry(frm)
        e.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=5)
        entries[lbl] = e

    # --- Load danh sách ---
    def load_employees():
        tree.delete(*tree.get_children())
        try:
            cursor.execute("SELECT manhanvien, hoten, vitri, luong, thuong, calam, hieusuat FROM nhanvien")
            for r in cursor.fetchall():
                tree.insert("", tk.END, values=r)
        except Exception as e:
            messagebox.showerror("Lỗi tải", str(e))

    # --- Thêm ---
    def add_employee():
        try:
            sql = """INSERT INTO nhanvien (hoten, vitri, luong, thuong, calam, hieusuat)
                     VALUES (%s,%s,%s,%s,%s,%s)"""
            vals = (
                entries["Họ tên"].get(),
                entries["Vị trí"].get(),
                float(entries["Lương"].get() or 0),
                float(entries["Thưởng"].get() or 0),
                entries["Ca làm"].get(),
                float(entries["Hiệu suất"].get() or 0)
            )
            cursor.execute(sql, vals)
            db_commit(conn)
            load_employees()
            messagebox.showinfo("Thành công", "Đã thêm nhân viên.")
        except Exception as e:
            messagebox.showerror("Lỗi thêm", str(e))

    # --- Cập nhật ---
    def update_employee():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Chọn nhân viên để sửa.")
            return
        manv = tree.item(sel)["values"][0]
        try:
            sql = """UPDATE nhanvien SET hoten=%s, vitri=%s, luong=%s, thuong=%s, calam=%s, hieusuat=%s
                     WHERE manhanvien=%s"""
            vals = (
                entries["Họ tên"].get(),
                entries["Vị trí"].get(),
                float(entries["Lương"].get() or 0),
                float(entries["Thưởng"].get() or 0),
                entries["Ca làm"].get(),
                float(entries["Hiệu suất"].get() or 0),
                manv
            )
            cursor.execute(sql, vals)
            db_commit(conn)
            load_employees()
            messagebox.showinfo("Thành công", "Đã cập nhật nhân viên.")
        except Exception as e:
            messagebox.showerror("Lỗi cập nhật", str(e))

    # --- Xóa ---
    def delete_employee():
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Chọn", "Chọn nhân viên để xóa.")
            return
        manv = tree.item(sel)["values"][0]
        if not messagebox.askyesno("Xác nhận", f"Xóa nhân viên {manv}?"):
            return
        try:
            cursor.execute("DELETE FROM nhanvien WHERE manhanvien=%s", (manv,))
            db_commit(conn)
            load_employees()
            messagebox.showinfo("Đã xóa", "Xóa thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi xóa", str(e))

        # --- Lưu (tự động thêm hoặc cập nhật) ---
    def save_employee():
        sel = tree.focus()
        try:
            if sel:  # có dòng được chọn → cập nhật
                manv = tree.item(sel)["values"][0]
                sql = """UPDATE nhanvien 
                         SET hoten=%s, vitri=%s, luong=%s, thuong=%s, calam=%s, hieusuat=%s
                         WHERE manhanvien=%s"""
                vals = (
                    entries["Họ tên"].get(),
                    entries["Vị trí"].get(),
                    float(entries["Lương"].get() or 0),
                    float(entries["Thưởng"].get() or 0),
                    entries["Ca làm"].get(),
                    float(entries["Hiệu suất"].get() or 0),
                    manv
                )
                cursor.execute(sql, vals)
                db_commit(conn)
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân viên.")
            else:  # chưa chọn → thêm mới
                sql = """INSERT INTO nhanvien (hoten, vitri, luong, thuong, calam, hieusuat)
                         VALUES (%s,%s,%s,%s,%s,%s)"""
                vals = (
                    entries["Họ tên"].get(),
                    entries["Vị trí"].get(),
                    float(entries["Lương"].get() or 0),
                    float(entries["Thưởng"].get() or 0),
                    entries["Ca làm"].get(),
                    float(entries["Hiệu suất"].get() or 0)
                )
                cursor.execute(sql, vals)
                db_commit(conn)
                messagebox.showinfo("Thành công", "Đã thêm nhân viên mới.")
            load_employees()
        except Exception as e:
            messagebox.showerror("Lỗi lưu", str(e))


    # --- Khi chọn dòng ---
    def on_select(ev):
        sel = tree.focus()
        if not sel:
            return
        v = tree.item(sel)["values"]
        entries["Họ tên"].delete(0, tk.END); entries["Họ tên"].insert(0, v[1])
        entries["Vị trí"].delete(0, tk.END); entries["Vị trí"].insert(0, v[2])
        entries["Lương"].delete(0, tk.END); entries["Lương"].insert(0, v[3])
        entries["Thưởng"].delete(0, tk.END); entries["Thưởng"].insert(0, v[4])
        entries["Ca làm"].delete(0, tk.END); entries["Ca làm"].insert(0, v[5])
        entries["Hiệu suất"].delete(0, tk.END); entries["Hiệu suất"].insert(0, v[6])

    # --- Nút chức năng ---
    btnf = tk.Frame(win)
    btnf.pack(pady=8)
    tk.Button(btnf, text="Thêm", command=add_employee, width=12).grid(row=0, column=0, padx=5)
    tk.Button(btnf, text="Cập nhật", command=update_employee, width=12).grid(row=0, column=1, padx=5)
    tk.Button(btnf, text="Xóa", command=delete_employee, width=12).grid(row=0, column=2, padx=5)
    tk.Button(btnf, text="Lưu", command=save_employee, width=12).grid(row=0, column=3, padx=5)
    tk.Button(btnf, text="Đóng", command=lambda:[cursor.close(), conn.close(), win.destroy()], width=12).grid(row=0, column=4, padx=5)

    tree.bind("<<TreeviewSelect>>", on_select)
    load_employees()
    win.mainloop()



# ---------------------------
# Main Menu
# ---------------------------
def main_menu():
    root = tk.Tk()
    root.title("MENU CHÍNH - QUẢN LÝ CỬA HÀNG TIVI")

    # ---- CANH GIỮA MÀN HÌNH ----
    window_width = 600
    window_height = 450

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    # --------------------------------

    root.resizable(False, False)

    tk.Label(root, text="QUẢN LÝ CỬA HÀNG TIVI", font=("Arial", 16, "bold")).pack(pady=20)
    tk.Button(root, text="Quản lý sản phẩm", width=30, height=2,
              command=lambda:[root.destroy(), open_product_manager()]).pack(pady=8)
    tk.Button(root, text="Quản lý kho hàng", width=30, height=2,
              command=lambda:[root.destroy(), open_stock_manager()]).pack(pady=8)
    tk.Button(root, text="Quản lý hóa đơn", width=30, height=2,
              command=lambda:[root.destroy(), open_invoice_manager()]).pack(pady=8)
    tk.Button(root, text="Quản lý khách hàng", width=30, height=2,
              command=lambda:[root.destroy(), open_customer_manager()]).pack(pady=8)
    tk.Button(root, text="Quản lý nhân viên", width=30, height=2,
              command=lambda:[root.destroy(), open_employee_manager()]).pack(pady=8)
    tk.Button(root, text="Thoát", width=30, height=2, command=root.destroy).pack(pady=8)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
