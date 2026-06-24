from database import SessionLocal, engine
import models
import auth

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
# 创建管理员
hash_pwd = auth.get_password_hash("123456")
admin = models.AdminUser(username="admin", password=hash_pwd)
db.add(admin)
db.commit()
print("管理员创建成功，账号admin，密码123456")