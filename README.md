Perfect 👍 Let me reformat my last explanation into a **README.md** style guide for you.

---

# Django Relationships – `related_name` Explained

When you define a relationship (`ForeignKey`, `OneToOneField`, `ManyToManyField`) in Django, you get **two directions** of access:

1. **Forward relation** → from the model that defines the field.
2. **Reverse relation** → from the related model back to this one.

The `related_name` option controls the **reverse relation name**.

---

## 🔹 Example 1: ForeignKey with `related_name`

```python
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")
```

* **Forward access (Book → User):**

  ```python
  book = Book.objects.first()
  print(book.author.username)
  ```

* **Reverse access (User → Book):**

  ```python
  user = User.objects.first()
  print(user.books.all())  # because related_name="books"
  ```

👉 Without `related_name`, Django defaults to:

```python
user.book_set.all()
```

---

## 🔹 Example 2: OneToOneField with `related_name`

```python
class Profile(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField()
```

* **Forward (Profile → User):**

  ```python
  profile = Profile.objects.first()
  print(profile.author.username)
  ```

* **Reverse (User → Profile):**

  ```python
  user = User.objects.first()
  print(user.profile.bio)  # reverse name is "profile"
  ```

👉 Without `related_name`, you’d still get `user.profile`, but if multiple `OneToOneField`s point to `User`, you need different names.

---

## 🔹 Example 3: ManyToManyField with `related_name`

```python
class Reader(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book, related_name="readers")
```

* **Forward (Reader → Book):**

  ```python
  reader = Reader.objects.first()
  print(reader.books.all())
  ```

* **Reverse (Book → Reader):**

  ```python
  book = Book.objects.first()
  print(book.readers.all())  # reverse name is "readers"
  ```

👉 Without `related_name`, Django defaults to:

```python
book.reader_set.all()
```

---

## ✅ Why use `related_name`?

1. **Cleaner, more meaningful code**

   ```python
   user.books.all()      # ✅ clear
   user.book_set.all()   # ❌ less readable
   ```

2. **Avoid name clashes**
   Example:

   ```python
   class Like(models.Model):
       user = models.ForeignKey(User, related_name="likes_given")
       post = models.ForeignKey(User, related_name="likes_received")
   ```

   Usage:

   ```python
   user.likes_given.all()
   user.likes_received.all()
   ```

3. **Match domain language**
   You can choose names that make sense for your business logic.

---

## ⚡ TL;DR

* **Forward access** → use the field name (`book.author`)
* **Reverse access** → use `related_name` (`user.books.all()`)
* **Without `related_name`** → Django makes one (`user.book_set.all()`)

---

📌 Use `related_name` whenever:

* You want **readable reverse relations**,
* You want to **avoid collisions**,
* You want names that **match your business domain**.

---

👉 Do you also want me to include a **visual diagram (tables + arrows)** in the README so you can see how forward and reverse lookups connect?
