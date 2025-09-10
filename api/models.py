from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserFile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="file")
    profile_pic = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s file"


# Now understanding the concept of the One to one field , foreign key , many to one and the many to many releation ship


# Author 👤

# Profile 🧾 (one-to-one with Author)

# Book 📚 (many-to-one with Author)

# Reader 👥 (many-to-many with Book)

# Then we’ll see:

# select_related (for One-to-One and ForeignKey)

# prefetch_related (for ManyToMany)

# and finally, build APIs (CRUD + related data).


class Profile(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField()
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.author.username}'s profile"


# now checking the foreign key  thing - one author can write the many books in his lifetime


class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="books")

    def __str__(self):
        return f"{self.title}"


# Many to many -> many book can be read by many readers


class Reader(models.Model):
    name = models.CharField(max_length=20)
    books = models.ManyToManyField(Book, related_name="readers")

    def __str__(self):
        return self.name
