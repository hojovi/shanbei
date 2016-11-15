create database if not exists shanbei default charset utf8 default collate utf8_general_ci;
use shanbei;

#单词表
create table if not exists word(
	id int primary key auto_increment,
	word varchar(100) unique key not null comment "单词",
	explanation text comment "解释",
	example text comment "例句"
)engine=innodb;

#标签表
create table if not exists tag(
	id int primary key auto_increment,
	tag varchar(50) unique key comment "标签"
)engine=innodb;

#用户表
create table if not exists user(
	id int primary key auto_increment,
	name varchar(50) unique key not null comment "用户名",
	password varchar(64) not null comment "密码",
	unique index name_password_index(name,password)
)engine=innodb;

#计划表
create table if not exists task(
	id int primary key auto_increment,
	userId int comment "用户ID",
	wordNumPerDay int comment "用户每日单词量",
	foreign key(userId) references user(id) on delete cascade on update cascade
)engine=innodb;
#历史任务完成情况表
create table if not exists history_task(
	id int primary key auto_increment,
	userId int comment "用户ID",
	taskTime date comment "任务时间",
	plan int comment "计划完成的单词量",
	complete int comment "已经完成的单词量",
	foreign key(userId) references user(id) on delete cascade on update cascade
)engine=innodb;

#进度表
create table if not exists progress(
	id int primary key auto_increment,
	userId int comment "用户ID",
	tagId int comment "标签ID",
	wordId int comment "单词ID",
	progress int comment "复习进度",
	foreign key(userId) references user(id) on delete cascade on update cascade,
	foreign key(wordId) references word(id) on delete cascade on update cascade
)engine=innodb;

#笔记表
create table if not exists note(
	id int primary key auto_increment,
	userId int comment "用户ID",
	wordId int comment "单词ID",
	note text comment "笔记内容",
	foreign key(userId) references user(id) on delete cascade on update cascade,
	foreign key(wordId) references word(id) on delete cascade on update cascade
)engine=innodb;

#单词标签关联表
create table if not exists word_tag(
	id int primary key auto_increment,
	wordId int comment "单词ID",
	tagId int comment "标签ID",
	foreign key(wordId) references word(id) on delete cascade on update cascade,
	foreign key(tagId) references tag(id) on delete cascade on update cascade
)engine=innodb;

#用户标签关联表
create table if not exists user_tag(
	id int primary key auto_increment,
	userId int comment "用户ID",
	tagId int comment "标签ID",
	foreign key(userId) references user(id) on delete cascade on update cascade,
	foreign key(tagId) references tag(id) on delete cascade on update cascade
)engine=innodb;