CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(256) NOT NULL, 
	profile_pic VARCHAR(200), 
	bio VARCHAR(500), 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);

CREATE TABLE blocks (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	blocker_id INTEGER NOT NULL, 
	blocked_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(blocker_id) REFERENCES users (id), 
	FOREIGN KEY(blocked_id) REFERENCES users (id)
);

CREATE TABLE followers (
	follower_id INTEGER, 
	following_id INTEGER, 
	FOREIGN KEY(follower_id) REFERENCES users (id), 
	FOREIGN KEY(following_id) REFERENCES users (id)
);

CREATE TABLE messages (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	sender_id INTEGER NOT NULL, 
	receiver_id INTEGER NOT NULL, 
	message VARCHAR(1000) NOT NULL, 
	timestamp DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sender_id) REFERENCES users (id), 
	FOREIGN KEY(receiver_id) REFERENCES users (id)
);

CREATE TABLE posts (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	image VARCHAR(200) NOT NULL, 
	caption VARCHAR(1000), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE comments (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	post_id INTEGER NOT NULL, 
	text VARCHAR(500) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(post_id) REFERENCES posts (id)
);

CREATE TABLE likes (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	post_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(post_id) REFERENCES posts (id)
);

