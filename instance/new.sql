BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "admission_record" (
	"id"	INTEGER NOT NULL,
	"patient_id"	INTEGER NOT NULL,
	"doctor_id"	INTEGER NOT NULL,
	"admission_date"	DATETIME,
	PRIMARY KEY("id"),
	FOREIGN KEY("doctor_id") REFERENCES "user"("id"),
	FOREIGN KEY("patient_id") REFERENCES "patient"("id")
);
CREATE TABLE IF NOT EXISTS "alembic_version" (
	"version_num"	VARCHAR(32) NOT NULL,
	CONSTRAINT "alembic_version_pkc" PRIMARY KEY("version_num")
);
CREATE TABLE IF NOT EXISTS "appointment" (
	"id"	INTEGER NOT NULL,
	"patient_request_id"	INTEGER NOT NULL,
	"provider_id"	INTEGER NOT NULL,
	"appointment_date"	DATETIME,
	"notes"	TEXT,
	PRIMARY KEY("id"),
	FOREIGN KEY("patient_request_id") REFERENCES "appointment_request"("id"),
	FOREIGN KEY("provider_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "appointment_request" (
	"id"	INTEGER NOT NULL,
	"patient_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"requested_time"	DATETIME NOT NULL,
	"reason"	VARCHAR(255),
	"status"	VARCHAR(20),
	"specialization_needed"	VARCHAR(100),
	PRIMARY KEY("id"),
	FOREIGN KEY("patient_id") REFERENCES "patient"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "audit_log" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"action"	VARCHAR(100) NOT NULL,
	"details"	TEXT NOT NULL,
	"timestamp"	DATETIME,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "bed" (
	"id"	INTEGER NOT NULL,
	"room_id"	INTEGER NOT NULL,
	"bed_number"	VARCHAR(10) NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("room_id") REFERENCES "room"("id")
);
CREATE TABLE IF NOT EXISTS "discharge_record" (
	"id"	INTEGER NOT NULL,
	"patient_id"	INTEGER NOT NULL,
	"doctor_id"	INTEGER NOT NULL,
	"discharge_date"	DATETIME,
	PRIMARY KEY("id"),
	FOREIGN KEY("doctor_id") REFERENCES "user"("id"),
	FOREIGN KEY("patient_id") REFERENCES "patient"("id")
);
CREATE TABLE IF NOT EXISTS "health_metrics" (
	"id"	INTEGER NOT NULL,
	"patient_id"	INTEGER NOT NULL,
	"metric_type"	VARCHAR(100) NOT NULL,
	"value"	FLOAT NOT NULL,
	"measurement_date"	DATETIME,
	PRIMARY KEY("id"),
	FOREIGN KEY("patient_id") REFERENCES "patient"("id")
);
CREATE TABLE IF NOT EXISTS "medical_record" (
	"id"	INTEGER NOT NULL,
	"patient_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"date"	DATETIME NOT NULL,
	"summary"	VARCHAR(200) NOT NULL,
	"details"	TEXT NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("patient_id") REFERENCES "patient"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "patient" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"first_name"	VARCHAR(100) NOT NULL,
	"last_name"	VARCHAR(100) NOT NULL,
	"dob"	DATE NOT NULL,
	"phone_number"	VARCHAR(15),
	"address"	VARCHAR(255),
	"is_admitted"	BOOLEAN,
	"room_id"	INTEGER,
	"bed_id"	INTEGER,
	PRIMARY KEY("id"),
	UNIQUE("user_id"),
	FOREIGN KEY("bed_id") REFERENCES "bed"("id"),
	FOREIGN KEY("room_id") REFERENCES "room"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "patient_record" (
	"id"	INTEGER NOT NULL,
	"patient_id"	INTEGER NOT NULL,
	"user_id"	INTEGER,
	"doctor_id"	INTEGER NOT NULL,
	"record_date"	DATETIME,
	"details"	TEXT NOT NULL,
	"disease"	VARCHAR(100),
	"prescribed_medicine"	VARCHAR(255),
	"notes"	TEXT,
	"follow_up_date"	DATE,
	"diagnosis"	TEXT,
	"treatment"	TEXT,
	"treatment_plan"	TEXT,
	PRIMARY KEY("id"),
	FOREIGN KEY("doctor_id") REFERENCES "user"("id"),
	FOREIGN KEY("patient_id") REFERENCES "patient"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "room" (
	"id"	INTEGER NOT NULL,
	"room_number"	VARCHAR(10) NOT NULL,
	"bed_count"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	UNIQUE("room_number")
);
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER NOT NULL,
	"username"	VARCHAR(150) NOT NULL,
	"email"	VARCHAR(150) NOT NULL,
	"password_hash"	VARCHAR(150) NOT NULL,
	"is_provider"	BOOLEAN,
	"is_active"	BOOLEAN,
	"role"	VARCHAR(50) NOT NULL,
	"specialization"	VARCHAR(50),
	"otp"	VARCHAR(6),
	"otp_expiration"	DATETIME,
	UNIQUE("email"),
	PRIMARY KEY("id"),
	UNIQUE("username")
);
INSERT INTO "alembic_version" VALUES ('b4900af7e218');
INSERT INTO "appointment" VALUES (1,2,8,'2024-11-13 13:32:00.000000','');
INSERT INTO "appointment" VALUES (2,2,8,'2024-11-13 13:32:00.000000','');
INSERT INTO "appointment" VALUES (3,1,8,'2024-11-20 13:37:00.000000','');
INSERT INTO "appointment" VALUES (4,1,8,'2024-11-20 13:37:00.000000','');
INSERT INTO "appointment" VALUES (5,3,8,'2024-11-13 16:24:00.000000','');
INSERT INTO "appointment" VALUES (6,5,8,'2024-12-04 12:00:00.000000','');
INSERT INTO "appointment" VALUES (7,6,8,'2024-12-07 16:40:00.000000','');
INSERT INTO "appointment" VALUES (8,6,8,'2024-11-25 12:15:00.000000','');
INSERT INTO "appointment" VALUES (9,7,8,'2024-11-28 13:43:00.000000','');
INSERT INTO "appointment" VALUES (10,8,11,'2024-11-30 22:30:00.000000','');
INSERT INTO "appointment_request" VALUES (1,2,13,'2024-11-13 12:19:00.000000','sdfghjk','pending','general_practitioner');
INSERT INTO "appointment_request" VALUES (2,2,13,'2024-11-14 13:27:00.000000','dtfghjk','pending','gynecologist');
INSERT INTO "appointment_request" VALUES (3,3,16,'2024-11-13 04:24:00.000000','check up','pending','general_practitioner');
INSERT INTO "appointment_request" VALUES (4,6,19,'2024-12-06 19:36:00.000000','To see a neurologist','pending','neurologist');
INSERT INTO "appointment_request" VALUES (5,6,19,'2024-12-04 12:00:00.000000','See the doc','pending','surgeon');
INSERT INTO "appointment_request" VALUES (6,9,25,'2024-12-07 16:40:00.000000','consultation','pending','orthopedist');
INSERT INTO "appointment_request" VALUES (7,11,28,'2024-11-28 13:40:00.000000','to see a doctor','pending','neurologist');
INSERT INTO "appointment_request" VALUES (8,11,28,'2024-11-30 10:30:00.000000','gfhbvn','pending','general_practitioner');
INSERT INTO "bed" VALUES (1,1,'1');
INSERT INTO "bed" VALUES (2,1,'2');
INSERT INTO "bed" VALUES (3,1,'3');
INSERT INTO "bed" VALUES (4,1,'4');
INSERT INTO "bed" VALUES (5,1,'5');
INSERT INTO "bed" VALUES (6,1,'6');
INSERT INTO "bed" VALUES (7,1,'7');
INSERT INTO "bed" VALUES (8,1,'8');
INSERT INTO "bed" VALUES (9,1,'9');
INSERT INTO "bed" VALUES (10,1,'10');
INSERT INTO "bed" VALUES (11,2,'1');
INSERT INTO "bed" VALUES (12,2,'2');
INSERT INTO "bed" VALUES (13,2,'3');
INSERT INTO "bed" VALUES (14,2,'4');
INSERT INTO "bed" VALUES (15,2,'5');
INSERT INTO "bed" VALUES (16,2,'6');
INSERT INTO "bed" VALUES (17,2,'7');
INSERT INTO "bed" VALUES (18,2,'8');
INSERT INTO "bed" VALUES (19,2,'9');
INSERT INTO "bed" VALUES (20,2,'10');
INSERT INTO "bed" VALUES (21,3,'1');
INSERT INTO "bed" VALUES (22,3,'2');
INSERT INTO "bed" VALUES (23,3,'3');
INSERT INTO "bed" VALUES (24,3,'4');
INSERT INTO "bed" VALUES (25,3,'5');
INSERT INTO "bed" VALUES (26,3,'6');
INSERT INTO "bed" VALUES (27,3,'7');
INSERT INTO "bed" VALUES (28,3,'8');
INSERT INTO "bed" VALUES (29,3,'9');
INSERT INTO "bed" VALUES (30,3,'10');
INSERT INTO "bed" VALUES (31,4,'1');
INSERT INTO "bed" VALUES (32,4,'2');
INSERT INTO "bed" VALUES (33,4,'3');
INSERT INTO "bed" VALUES (34,4,'4');
INSERT INTO "bed" VALUES (35,4,'5');
INSERT INTO "bed" VALUES (36,4,'6');
INSERT INTO "bed" VALUES (37,4,'7');
INSERT INTO "bed" VALUES (38,4,'8');
INSERT INTO "bed" VALUES (39,4,'9');
INSERT INTO "bed" VALUES (40,4,'10');
INSERT INTO "bed" VALUES (41,5,'1');
INSERT INTO "bed" VALUES (42,5,'2');
INSERT INTO "bed" VALUES (43,5,'3');
INSERT INTO "bed" VALUES (44,5,'4');
INSERT INTO "bed" VALUES (45,5,'5');
INSERT INTO "bed" VALUES (46,5,'6');
INSERT INTO "bed" VALUES (47,5,'7');
INSERT INTO "bed" VALUES (48,5,'8');
INSERT INTO "bed" VALUES (49,5,'9');
INSERT INTO "bed" VALUES (50,5,'10');
INSERT INTO "bed" VALUES (51,6,'1');
INSERT INTO "bed" VALUES (52,6,'2');
INSERT INTO "bed" VALUES (53,6,'3');
INSERT INTO "bed" VALUES (54,6,'4');
INSERT INTO "bed" VALUES (55,6,'5');
INSERT INTO "bed" VALUES (56,6,'6');
INSERT INTO "bed" VALUES (57,6,'7');
INSERT INTO "bed" VALUES (58,6,'8');
INSERT INTO "bed" VALUES (59,6,'9');
INSERT INTO "bed" VALUES (60,6,'10');
INSERT INTO "bed" VALUES (61,7,'1');
INSERT INTO "bed" VALUES (62,7,'2');
INSERT INTO "bed" VALUES (63,7,'3');
INSERT INTO "bed" VALUES (64,7,'4');
INSERT INTO "bed" VALUES (65,7,'5');
INSERT INTO "bed" VALUES (66,7,'6');
INSERT INTO "bed" VALUES (67,7,'7');
INSERT INTO "bed" VALUES (68,7,'8');
INSERT INTO "bed" VALUES (69,7,'9');
INSERT INTO "bed" VALUES (70,7,'10');
INSERT INTO "bed" VALUES (71,8,'1');
INSERT INTO "bed" VALUES (72,8,'2');
INSERT INTO "bed" VALUES (73,8,'3');
INSERT INTO "bed" VALUES (74,8,'4');
INSERT INTO "bed" VALUES (75,8,'5');
INSERT INTO "bed" VALUES (76,8,'6');
INSERT INTO "bed" VALUES (77,8,'7');
INSERT INTO "bed" VALUES (78,8,'8');
INSERT INTO "bed" VALUES (79,8,'9');
INSERT INTO "bed" VALUES (80,8,'10');
INSERT INTO "bed" VALUES (81,9,'1');
INSERT INTO "bed" VALUES (82,9,'2');
INSERT INTO "bed" VALUES (83,9,'3');
INSERT INTO "bed" VALUES (84,9,'4');
INSERT INTO "bed" VALUES (85,9,'5');
INSERT INTO "bed" VALUES (86,9,'6');
INSERT INTO "bed" VALUES (87,9,'7');
INSERT INTO "bed" VALUES (88,9,'8');
INSERT INTO "bed" VALUES (89,9,'9');
INSERT INTO "bed" VALUES (90,9,'10');
INSERT INTO "bed" VALUES (91,10,'1');
INSERT INTO "bed" VALUES (92,10,'2');
INSERT INTO "bed" VALUES (93,10,'3');
INSERT INTO "bed" VALUES (94,10,'4');
INSERT INTO "bed" VALUES (95,10,'5');
INSERT INTO "bed" VALUES (96,10,'6');
INSERT INTO "bed" VALUES (97,10,'7');
INSERT INTO "bed" VALUES (98,10,'8');
INSERT INTO "bed" VALUES (99,10,'9');
INSERT INTO "bed" VALUES (100,10,'10');
INSERT INTO "patient" VALUES (1,9,'genzy','Moses','2024-09-29','07324678909','qfwgethry',1,10,40);
INSERT INTO "patient" VALUES (2,13,'genzy','Moses','2002-08-08','07324678909','SDFGHJK',1,4,36);
INSERT INTO "patient" VALUES (3,16,'Alice','ambassador ','2003-02-03','07324678909','SDFGHJK',1,NULL,NULL);
INSERT INTO "patient" VALUES (4,17,'Gunny','Moses','2007-02-02','09324678909','SDFGHJK',0,NULL,NULL);
INSERT INTO "patient" VALUES (5,18,'Riggy G','Murima','1967-08-24','0722463455','UsiguzeMurima',1,10,91);
INSERT INTO "patient" VALUES (6,19,'Ken ','Chonga','2022-11-08','0745467810','FGHHHHF',0,NULL,NULL);
INSERT INTO "patient" VALUES (7,20,'Don','G','2007-10-18','0765453211','Kilifi',0,NULL,NULL);
INSERT INTO "patient" VALUES (8,21,'Hassan','Hassan','2010-12-19','076432145','Kericho',0,NULL,NULL);
INSERT INTO "patient" VALUES (9,25,'Kilonzo','Kilonzo','2004-04-19','0789675432','Kitui',0,NULL,NULL);
INSERT INTO "patient" VALUES (10,26,'Ole','Sapit','1949-05-30','0734211156','Eldoret',1,1,4);
INSERT INTO "patient" VALUES (11,28,'Paul','Paul','2024-10-29','0977654256','Siwaka',0,NULL,NULL);
INSERT INTO "patient" VALUES (12,6,'ke7','ke7','2000-01-01',NULL,NULL,0,NULL,NULL);
INSERT INTO "patient_record" VALUES (1,1,NULL,8,'2024-11-02 09:21:55.819562','','Headache ','take panadol','nkerkjdvkmnv','2024-12-10','vhbjknl;','cxvbnm,','xvcnm,');
INSERT INTO "patient_record" VALUES (2,1,NULL,8,'2024-11-02 09:23:12.938210','','Headache ','take panadol','nkerkjdvkmnv','2024-12-02',NULL,NULL,NULL);
INSERT INTO "patient_record" VALUES (3,4,9,8,'2024-11-18 13:46:00.223661','szdfghjkl','Headache ','cxvbnm,.','zxcvbnm,.','2024-11-18','sfdghjkl','dfghjk','cvbnm,.');
INSERT INTO "patient_record" VALUES (4,2,13,8,'2024-11-18 15:50:25.972427','fxcghvjkl','Headache ','cvvxcbnm','cxvbnm,.','2024-11-18','dasfghjkl','fghjkl;','cxvbnm,.');
INSERT INTO "patient_record" VALUES (5,3,16,8,'2024-11-18 15:59:47.426731','fdghjk','xvchjk','xzcvbnm,.','dzxfcgvhjbn','2024-11-19','dzfxgchjkl','fxcgvhjk','xfcgvhjzdxfgchvjkl');
INSERT INTO "patient_record" VALUES (6,3,16,8,'2024-11-18 16:07:19.704776','fdghjk','xvchjk','xzcvbnm,.','dzxfcgvhjbn','2024-11-19','dzfxgchjkl','fxcgvhjk','xfcgvhjzdxfgchvjkl');
INSERT INTO "patient_record" VALUES (7,6,19,8,'2024-11-18 16:08:49.018814','xfcgvhbjnkm','dfghjkl','dfxcgvhjkdsfgh','xcvjfghjklsdfg','2024-11-19','dsfghjkl','hhhhhhhhhhhhhhhhhh','sadfghjkl');
INSERT INTO "patient_record" VALUES (8,5,18,8,'2024-11-18 16:23:43.874199','uyui','vbnm','hhgj','retyu','2024-11-22','vbnmghj','ghjk','tyui');
INSERT INTO "patient_record" VALUES (9,8,21,8,'2024-11-19 13:58:24.747784','ertyui','sdfghjk','sdfghj','retyuio','2024-11-30','sfdgh','etryui','srtyui');
INSERT INTO "patient_record" VALUES (10,8,21,8,'2024-11-19 14:14:24.427605','ertyui','sdfghjk','sdfghj','retyuio','2024-11-30','sfdgh','etryui','srtyui');
INSERT INTO "patient_record" VALUES (11,9,25,8,'2024-11-20 08:21:25.641093','dtyugjh','Fever','rtyukl','dtyyiuoi','2024-11-22','sfdghj','cvbn','come for checkup after 1 month');
INSERT INTO "patient_record" VALUES (12,10,26,8,'2024-11-20 10:24:01.067047','sdfgh','asdfgh','sadfgh','dsfy','2024-11-23','asdfg','ewrtyu','sdfghj');
INSERT INTO "patient_record" VALUES (13,10,26,8,'2024-11-20 10:24:42.939110','zxcvb','werty','dfgh','zxcvbn','2024-11-24','ertyu','werty','dfghj');
INSERT INTO "patient_record" VALUES (14,11,28,11,'2024-11-25 14:21:22.916980','tryuio','retryui','wertyui','retyuio','2024-11-28','wertyuio','dsfghjk','sdfghj');
INSERT INTO "patient_record" VALUES (15,12,6,8,'2024-11-26 06:53:24.220029','vbn','fdgh','yuio','vbnvb','2024-11-28','ghj','gfhjk','zxcv');
INSERT INTO "room" VALUES (1,'A101',10);
INSERT INTO "room" VALUES (2,'A102',10);
INSERT INTO "room" VALUES (3,'A103',10);
INSERT INTO "room" VALUES (4,'A104',10);
INSERT INTO "room" VALUES (5,'B201',10);
INSERT INTO "room" VALUES (6,'B202',10);
INSERT INTO "room" VALUES (7,'B203',10);
INSERT INTO "room" VALUES (8,'B204',10);
INSERT INTO "room" VALUES (9,'C301',10);
INSERT INTO "room" VALUES (10,'C302',10);
INSERT INTO "user" VALUES (1,'admin_user','admin@example.com','scrypt:32768:8:1$83FwXzDa5BpM58Th$120c883cc01ace0ea4368defad8998e85a252827d0f393ec075f490ae72f26b1b32d90fe1d37b40725c4c403b6252ba23a503fa44590066dc200c9b07cf2fb7d',0,1,'admin',NULL,NULL,NULL);
INSERT INTO "user" VALUES (4,'admin20_user','admin02@example.com','scrypt:32768:8:1$jNIXU6dTB7fJU5cl$cc53114ddffaa0a93b18a090ef6757002f877295b23e600cd8c1312527eeafe3357f570532709ed710584cb109d1a55cb9a3b627d88d73e5941496bc8930e464',0,1,'admin',NULL,NULL,NULL);
INSERT INTO "user" VALUES (5,'kelvin1@gmail.com','kelvin@gmail.com','scrypt:32768:8:1$YOSz8ud2b2ne3YSO$b4c3867b7b0f93c9f1288647daefdfffa48f431ab677803e6ecc9bff7deb29715b12887b554023213dec2e5b63ce6bdbc2a86c801a6959dacf8f79d1685031a1',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (6,'ke7','kelvin22@gmail.com','scrypt:32768:8:1$jNIXU6dTB7fJU5cl$cc53114ddffaa0a93b18a090ef6757002f877295b23e600cd8c1312527eeafe3357f570532709ed710584cb109d1a55cb9a3b627d88d73e5941496bc8930e464',0,1,'admin',NULL,NULL,NULL);
INSERT INTO "user" VALUES (8,'137432','yegonb@gmail.com','scrypt:32768:8:1$3SY1UV41UlWCHFpK$6ca0d7a3aa90fb29fed8860c6e53c5ef70173b2ffcf0abdc1cd124652138926845c5f8241592831051c114545536e0618685e75aa0a96f1dc3a1853b06e117ab',1,1,'doctor','orthopedist',NULL,NULL);
INSERT INTO "user" VALUES (9,'yegonb@gmail.com','admin3@example.com','scrypt:32768:8:1$DOeDfbwNpb50V6mT$ff77a26881cf1900585b6646dce27b707eafa330c6bd1ffb33040730e69e6f1ec4d5756f242c5646b9756907346d2693f39de16073dc36ec7f220551c1181b1f',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (10,'John','john@gmail.com','scrypt:32768:8:1$tpSxXzZsNdNP8ugW$4df03273a7ff094cf9f02463fb4b9de0cbfcbf76ca62c5484ff77e14f6923d711e0d121b0c15fcd2d1be318f660deca234cd2adc105a3d8933d8a32884e6dd37',1,1,'admin','general_practitioner',NULL,NULL);
INSERT INTO "user" VALUES (11,'Liz','liz@gmail.com','scrypt:32768:8:1$vSJDkpF4FxjnAKKE$128f0fac8c937a60cdd2de01768c872f9732fec64e39fddf141058a8cb0f8ffb46ddc44e95b4e916a2a15aa01f3d1072880a84436596799fa3606a5c48118279',1,1,'doctor','neurologist',NULL,NULL);
INSERT INTO "user" VALUES (12,'Kiptoo','kiptoo@gmail.com','scrypt:32768:8:1$GPGKQ9XxQQPlGUSN$e6c9819e53dfb638bbeccc03ad20bad385a547a93a53c063a1cbfaf30d145376cafeb9c951f44d064595c242063306f2955a67282804e8a935dde120d761b965',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (13,'brian','kiptoob@gmail.com','scrypt:32768:8:1$rCTlf6H9etkPGiCQ$30bec0235de22bd21655c5ce461c6381f7c9fc065aced3c012d009aeeca81b1f92e7a1f589e57c691376248ca7034816dcb0dcfc2dfb7342293f2307c89cc0a8',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (14,'kelvin','kelvin3@gmail.com','scrypt:32768:8:1$sbCKq1QVShAK1wbm$33f2c434f5456f292548121d2274a58f8dd0e170640642c0abaa239b9982cbef0051b18eab970db2c1902b14877570348db246ed8023fe7d5abeaf20415153ce',1,1,'admin','surgeon',NULL,NULL);
INSERT INTO "user" VALUES (15,'Alvin','alvin@gmail.com','scrypt:32768:8:1$jNIXU6dTB7fJU5cl$cc53114ddffaa0a93b18a090ef6757002f877295b23e600cd8c1312527eeafe3357f570532709ed710584cb109d1a55cb9a3b627d88d73e5941496bc8930e464',1,1,'nurse','general_practitioner',NULL,NULL);
INSERT INTO "user" VALUES (16,'hjdgfaj','gunny.odhiambo@strathmore.edu','scrypt:32768:8:1$nlTbzf7dNASz1ZuZ$a5e2ab9aff84093ed8d335ede2b8911e21948776a0f761b3d8ac09fcebed804040e2433d5bfcd4275845b65ec86efbaae0c704346ea63e5c474d9ff41f023583',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (17,'kelvin.kipkemboi@strathmore.edu','kelvin.kipkemboi@strathmore.edu','scrypt:32768:8:1$A6Y2AHQ3Zh01kCz0$40b48431ab3f1543bcecf0eb3138309d7fae1ca7b192f294bb1bafda3e158166f34cc870819a46e461f1bff89a534f624f8a778b239db1cf1985bc80e9c97336',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (18,'Riggy G','murima@gmail.com','scrypt:32768:8:1$i7652KCimgDvhiiQ$9698d8f4656f5ca50056195a9a3d90ece2c592a06f53e9af6028c5c16f3191538f857ba59df421162ae3c9ab4f63ee28a32eb40040c2f6a67df2ec723cc0526c',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (19,'chonga@gmail.com','chonga@gmail.com','scrypt:32768:8:1$m3o5AunZxnPgvvCC$8c71fa20042b189f65cd8a8a798085556907df13180863a156908666513d732b7c6880d564283abeede227d5f0220e29302671a2cc5d9a0bea9c3cf80f16041e',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (20,'gle@gmail.com','gle@gmail.com','scrypt:32768:8:1$oljubyjtIbdDlOBl$3c1a9bf737bbd42cb09373e867a8363d47d981e1c6b5f33c9f9aca14c53af95e79c7bfd2d4739c4a30a996de50d4c80c9e2d7432266a565d421242730953a6f9',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (21,'hassan@gmail.com','hassan@gmail.com','scrypt:32768:8:1$Za2fqlO1adRX0Pff$5cb535c2291be82b3821ba674872849d0dacf10c479f1044d0a3c999175cd73889d203c1fab664e181d2f23a4ed7cfaabbdcdffeda6eeb8933e784a4b0e7d1f3',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (22,'Elizabeth','elizabeth@gmail.com','scrypt:32768:8:1$1OuvYQeMh5mjEEnu$a2374422ef20228ae01b2b3a1bcad5a032c05dcfa0e311506f4f29eadb3c419d5e2281516e69f9ad1ebfb96dfb6a2d70a9dd3acf38ef9458691717dfdbc8645a',1,1,'nurse','general_practitioner',NULL,NULL);
INSERT INTO "user" VALUES (23,'Morgan','morgan@gmail.com','scrypt:32768:8:1$Qq0Wk9WjtTyyL8WP$c907a0b0e9598b2ae4d072d60dee5e9d6c6329bb30c4d59960b6bfc4901948a7d2aa2a31f9ac14dc342958404b610de76cc0b30978ebb900ea7060cc9805f4df',1,1,'doctor','dermatologist',NULL,NULL);
INSERT INTO "user" VALUES (24,'Leone','leone@gmail.com','scrypt:32768:8:1$rvKX1hSXPb0J5QcN$5b9f53591264d90c1111483efe732afb631d69fb39140e93f8a7f9b1691d86015b8f705f50f266a7ac9066a549ceefd7a83706bad5037e3086f0f7be5a4cac07',1,1,'doctor','general_practitioner',NULL,NULL);
INSERT INTO "user" VALUES (25,'kilonzo@gmail.com','kilonzo@gmail.com','scrypt:32768:8:1$QRSfCo1uynydDajS$7b82a7c62b0ff2eccb03c40bf996ee5a2ced1527d55752bda186976268d8ed376fab67b5df7c8a49f55ad505d7fc956046e9aeaf348917beda68055184bc5009',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (26,'sapit@gmail.com','sapit@gmail.com','scrypt:32768:8:1$PIRzIEnN3BPQlXPE$f276dc6436a2c6b4e480ad3a882d4a78409495296c72b22223b9845967a9c829be6aa0e877dad10bad7e9bba5a1ca24d1fc28eb9b5fc6c872eb159bdea9c25d6',0,1,'patient',NULL,NULL,NULL);
INSERT INTO "user" VALUES (27,'Maingi Maingi','maingi@gmail.com','scrypt:32768:8:1$wOX6uPScDWWvcJz8$985b0c2dc89ad9f9b801308155a1f15430031b475d05cdef63d321f91c6b758aa2853bc834a0dcb0cd42d6bfb317b6d303b2fca6b6fe361b8eac5e89e6c6e767',1,1,'admin','general_practitioner',NULL,NULL);
INSERT INTO "user" VALUES (28,'paul@gmail.com','paul@gmail.com','scrypt:32768:8:1$h6lpV4tuLY5yVXeT$e303ca6f0f480955f9db16456c59c78318090f51ff7f8ac8d8e984004d81a36fe7dc1c3ea7656dea881165ea50abf29b0400f8a82eb117c02b19c5d95807cac5',0,1,'patient',NULL,NULL,NULL);
COMMIT;
