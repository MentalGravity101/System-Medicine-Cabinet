BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "door_logs" (
	"username"	TEXT NOT NULL,
	"accountType"	TEXT NOT NULL,
	"position"	TEXT NOT NULL,
	"date"	DATE NOT NULL,
	"time"	TIME NOT NULL,
	"action_taken"	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "medicine_inventory" (
	"name"	TEXT NOT NULL,
	"type"	TEXT NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"unit"	TEXT NOT NULL,
	"date_stored"	DATE NOT NULL,
	"expiration_date"	DATE
);
CREATE TABLE IF NOT EXISTS "users" (
	"username"	TEXT NOT NULL,
	"position"	TEXT NOT NULL,
	"accountType"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"qr_code"	BLOB
);
INSERT INTO "door_logs" VALUES ('admin1','admin','BHW','2024-1-21','09:15:01','UNLOCK');
INSERT INTO "door_logs" VALUES ('admin1','admin','BHW','2024-1-21','09:20:30','LOCK');
INSERT INTO "door_logs" VALUES ('staff4','admin','BNS','2024-5-16','14:30:00','UNLOCK');
INSERT INTO "door_logs" VALUES ('staff4','admin','BNS','2024-5-16','15:00:00','LOCK');
INSERT INTO "door_logs" VALUES ('staff1','admin','Midwife','2025-11-22','03:51:09','UNLOCK');
INSERT INTO "door_logs" VALUES ('staff1','admin','Midwife','2025-11-22','03:57:23','LOCK');
INSERT INTO "door_logs" VALUES ('admin2','admin','Midwife','2024-02-14','10:05:15','UNLOCK');
INSERT INTO "door_logs" VALUES ('admin2','admin','Midwife','2024-02-14','10:10:45','LOCK');
INSERT INTO "door_logs" VALUES ('staff2','staff','BNS','2024-03-03','11:25:33','UNLOCK');
INSERT INTO "door_logs" VALUES ('staff2','staff','BNS','2024-03-03','11:35:01','LOCK');
INSERT INTO "door_logs" VALUES ('admin3','admin','BHW','2024-07-21','08:50:12','UNLOCK');
INSERT INTO "door_logs" VALUES ('admin3','admin','BHW','2024-07-21','09:00:45','LOCK');
INSERT INTO "door_logs" VALUES ('staff3','staff','Midwife','2025-01-15','07:22:50','UNLOCK');
INSERT INTO "door_logs" VALUES ('staff3','staff','Midwife','2025-01-15','07:30:23','LOCK');
INSERT INTO "door_logs" VALUES ('admin4','admin','BNS','2025-04-30','12:45:30','UNLOCK');
INSERT INTO "door_logs" VALUES ('admin4','admin','BNS','2025-04-30','12:55:10','LOCK');
INSERT INTO "door_logs" VALUES ('staff5','staff','BHW','2025-08-09','16:40:00','UNLOCK');
INSERT INTO "door_logs" VALUES ('staff5','staff','BHW','2025-08-09','16:50:30','LOCK');
INSERT INTO "door_logs" VALUES ('admin5','admin','Midwife','2025-10-11','13:15:15','UNLOCK');
INSERT INTO "door_logs" VALUES ('admin5','admin','Midwife','2025-10-11','13:25:55','LOCK');
INSERT INTO "door_logs" VALUES ('staff6','staff','BNS','2026-02-28','18:05:45','UNLOCK');
INSERT INTO "door_logs" VALUES ('staff6','staff','BNS','2026-02-28','18:12:33','LOCK');
INSERT INTO "door_logs" VALUES ('admin6','admin','BHW','2026-05-16','14:35:09','UNLOCK');
INSERT INTO "door_logs" VALUES ('admin6','admin','BHW','2026-05-16','14:45:48','LOCK');
INSERT INTO "door_logs" VALUES ('staff7','staff','Midwife','2026-11-20','09:50:27','UNLOCK');
INSERT INTO "door_logs" VALUES ('staff7','staff','Midwife','2026-11-20','10:00:00','LOCK');
INSERT INTO "medicine_inventory" VALUES ('Biogesic','Paracetamol',100,'tablet','2024-8-16','2026-12-31');
INSERT INTO "medicine_inventory" VALUES ('Amoxicillin','Antibiotic',200,'capsule','2024-7-10','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Cetirizine','Antihistamine',150,'tablet','2024-6-5','2025-11-30');
INSERT INTO "medicine_inventory" VALUES ('Metformin','Antidiabetic',250,'tablet','2024-8-1','2025-10-31');
INSERT INTO "medicine_inventory" VALUES ('Ibuprofen','Analgesic',300,'tablet','2024-9-1','2026-01-31');
INSERT INTO "medicine_inventory" VALUES ('Loratadine','Antihistamine',180,'tablet','2024-7-20','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Amlodipine','Antihypertensive',120,'tablet','2024-7-15','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Simvastatin','Antihyperlipidemic',160,'tablet','2024-8-10','2026-03-31');
INSERT INTO "medicine_inventory" VALUES ('Ciprofloxacin','Antibiotic',140,'tablet','2024-6-10','2025-09-30');
INSERT INTO "medicine_inventory" VALUES ('Hydrochlorothiazide','Diuretic',110,'tablet','2024-5-25','2025-08-31');
INSERT INTO "medicine_inventory" VALUES ('Omeprazole','Proton Pump Inhibitor',220,'capsule','2024-8-5','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Losartan','Antihypertensive',200,'tablet','2024-7-30','2026-02-28');
INSERT INTO "medicine_inventory" VALUES ('Furosemide','Diuretic',130,'tablet','2024-7-12','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Pantoprazole','Proton Pump Inhibitor',170,'tablet','2024-8-8','2025-10-31');
INSERT INTO "medicine_inventory" VALUES ('Ranitidine','Antacid',90,'tablet','2024-6-18','2026-05-31');
INSERT INTO "medicine_inventory" VALUES ('Azithromycin','Antibiotic',100,'tablet','2024-8-22','2026-12-31');
INSERT INTO "medicine_inventory" VALUES ('Mefenamic Acid','NSAID',190,'tablet','2024-7-5','2025-09-30');
INSERT INTO "medicine_inventory" VALUES ('Doxycycline','Antibiotic',80,'capsule','2024-7-8','2025-11-30');
INSERT INTO "medicine_inventory" VALUES ('Salbutamol','Bronchodilator',70,'inhaler','2024-6-2','2026-06-30');
INSERT INTO "medicine_inventory" VALUES ('Aspirin','Antiplatelet',260,'tablet','2024-8-12','2026-12-31');
INSERT INTO "medicine_inventory" VALUES ('Clindamycin','Antibiotic',210,'capsule','2024-8-14','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Cefalexin','Antibiotic',170,'capsule','2024-7-25','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Prednisone','Corticosteroid',230,'tablet','2024-8-3','2026-03-31');
INSERT INTO "medicine_inventory" VALUES ('Montelukast','Leukotriene Inhibitor',150,'tablet','2024-7-28','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Warfarin','Anticoagulant',140,'tablet','2024-8-9','2025-11-30');
INSERT INTO "medicine_inventory" VALUES ('Methotrexate','Immunosuppressant',60,'tablet','2024-7-4','2026-02-28');
INSERT INTO "medicine_inventory" VALUES ('Levothyroxine','Thyroid Hormone',190,'tablet','2024-8-17','2026-12-31');
INSERT INTO "medicine_inventory" VALUES ('Rosuvastatin','Antihyperlipidemic',220,'tablet','2024-8-11','2026-01-31');
INSERT INTO "medicine_inventory" VALUES ('Citalopram','Antidepressant',130,'tablet','2024-8-2','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Escitalopram','Antidepressant',150,'tablet','2024-8-7','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Glibenclamide','Antidiabetic',200,'tablet','2024-8-6','2026-12-31');
INSERT INTO "medicine_inventory" VALUES ('Metoprolol','Beta-blocker',160,'tablet','2024-8-13','2026-02-28');
INSERT INTO "medicine_inventory" VALUES ('Alendronate','Osteoporosis Treatment',100,'tablet','2024-7-14','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Lisinopril','ACE Inhibitor',180,'tablet','2024-7-22','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Spironolactone','Diuretic',120,'tablet','2024-7-26','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Gabapentin','Anticonvulsant',200,'capsule','2024-7-17','2025-12-31');
INSERT INTO "medicine_inventory" VALUES ('Biogesic','Paracetamol',30,'tablet','2024-9-14','2027-11-1');
INSERT INTO "medicine_inventory" VALUES ('Biogesic','Paracetamol',30,'tablet','2024-9-14','2027-11-1');
INSERT INTO "medicine_inventory" VALUES ('Biogesic','Paracetamol',15,'capsule','2023-1-21','2024-12-12');
INSERT INTO "medicine_inventory" VALUES ('Biogesic','Paracetamol',15,'capsule','2024-1-21','2024-10-12');
INSERT INTO "users" VALUES ('admin1','Midwife','Admin','admin1',X'89504e470d0a1a0a0000000d494844520000012200000122010000000075c5e21b0000017a49444154789ced9a416e83301045dfd448591a290782abf548bd011ca537c0cb488e7e178694aa8b76132078bc42e649fe1ac6e6cf8089bfc7f8f60f089c72ca29a79c3a3a65f36860b406ebd332d3efaaab0aaa93244d607dbc19102449fa496dafab0a2a3d721cd000946db0b7aebaa87491f59baee854191ab8dba62bd64b2dc74a1490806eba660358175d47557f0a6a3433b316ac2f13f76273f6d6756aaae4fd3ac7e3cde66db0a7ae7a28eb01480d40106371fa9ef74fa52836be9b804e190d51a29b8278987c0d4755ffdad42af6d204d2ea01cc773df6cfa196e8c60c4469ae709792d663bf0515247d9ae9bd05480d1a62c6fabd759d989afd7d37014461dd746f800010647be9aa812ab15ffc4cc81a2dc8ba8fd644b2c57c1e55fd6b53cbbbb6f4318324652066709fb311f5ddc74c9787c5b9b9bfdf941adbf9c27a82f7ef37a54a81951ad67be100ba4e48fdea6392aeb9389eb10d79375d3550ac3f0d2e87cc5cd72a7b6df54ccafcdf28a79c72caa92aa82ff28bcce9866d57030000000049454e44ae426082');
INSERT INTO "users" VALUES ('johnpaul','BHW','Staff','johnpaul508663',X'89504e470d0a1a0a0000000d494844520000012200000122010000000075c5e21b0000018449444154789cedd9416e83301085e1ff15a42e9d1bf428f866556f0647e90de26525d0eb0293b4cda25d3418396607faa43c45a3f130c8fc7e4d4f7f40d054534d35d5d4d195f2d5a3982448db935834d743a8c1b67d06bf9d3a2bd2d9b6fd5ded9feb2154ca35aed7737e22a92f9fab66d5ffb8f7f432dff7179b6aaabcdaea3e1848200298045f5fba8e9abe0a3549924ec0f0dea3c8b28e39a57355add6babfd6b8498bfcbdea8f9bbe06a5987a20494c2f338a2c82d4a3583457dd8aeb186f7b5e6f3dd219e8bc0efee351d357a23a2b5e0b1d60f07ca3f6cf55b1ca73ce302ecac30ea0c18b3c9dcee5723d82da7a4ec835ee916eeb39e1d2828e9abe06659ff30247affe10b088e1fdd98a4573d5adf8ba325b4f5880e076d6de5de5ff3eef313bafc3ce08780c76eb393ba86d8fc9a43cec681df20be7aa59fddc6302dd7aec8af4dcf6f77b2a4500520f848ff6dd6a0f15ecb5cbdb338a61be4c9b6573d5ac6ee79c90bf1e325c0ee176d6de45ddee3181eb1bae4be56aaaa9a69a6aea7fd52767fccd46a763e16e0000000049454e44ae426082');
INSERT INTO "users" VALUES ('val','Midwife','Staff','val123',X'89504e470d0a1a0a0000000d494844520000012200000122010000000075c5e21b0000018b49444154789cedd8416eab301485e1ff14e68e9405642978675577064be90ef0b092a3f30640d2e6557a9df04c637b8012f4491c5997f8e6cafc7b4d2f3f40d054534d35d5d4d195d6d5c32449316d7762d15c55a8c1b63d835e6d039dede553d15c55a8b4d6b8df2401b0bc06a573d5a582ff6e3b8f90ebf954fff05dd0e75d9fd8d4b6b6bd0f0612dc6bfe73f51f35fd53a849927402c5d4035c9736a774aea7564bdd7fa9f60fadaf41c95cf528c5d4b3967ceaf10828726d75bfa7626de343c663b021d8f6dcd963c86be33f1e35fdef56ebde0f7377fb95e9cc70fb5bd5f67e77359d58f69961068fa9c7767e50ff3f5705ca9eaff29824bf5d328ab05c0ae77a6ef5a5bf0f46c3bbf074f9904967ab54ae1ad4b2f75b3fd3654f97dcc3d6e417cb5583dace5a6fdd8d67809059263bedacdd5f6d734c456e67ed7b9b63eeaa1e6769267599613e67e02a97ca55a3520414434631d88abb3fb15ef5cd1c3363d2399b74a2d5fdfeea3ec75c86997cbe1c3efd2f55dfcc316fc57fbf7dd4f44d35d554534dfd54fd013af5b4d63f6dfea50000000049454e44ae426082');
INSERT INTO "users" VALUES ('ruj','BHW','Staff','ruj123',X'89504e470d0a1a0a0000000d494844520000012200000122010000000075c5e21b0000018b49444154789ced99417283300c459f0a33599a1be428e66a3d526f0047c90df0b233cefc2e6c129a4dbb219020af90fd66f8230b23c926fe1ee3c73f2070ca29a79c726aef94d5d1623d00699ee937d575082a4a9226d0a7b5008d2449bfa9e7eb3a04956e311e7299312bbbb0adae2351d6a7dbc1f39c373a751f73dc3fef8d47a5e663250848005c5b91605974ed55fd5b50a399997540bc9c643dd792e66cadebada912f7cb180fdf563f832d751d81a2a4925112710208190d0084baa061afea5f9b624ee37f25f451190df39cfb7e1d6ae1fb1af780345137c07dbf3625e9db18cfb954b88c5d53f6c3fa4d75bd37d52e8d542d03105ce7d5bdaa7f6dca1eee4e0c9a6cd02c2b2cbf3b5991baf7316b5d1b72c9f937d67508eadec71c921971ba1a848cf5dbea7a6b6a3ed15307f10b2c4e1d227558bc781f7355aa7db035766071c8adc673f67fed9ad4a3ef016adcc3c9ef4e9e4105a97412e2d4d4fcfe566aed5ffd6b522c3a09502b2a4a8b616abc9fb326f5d8c7d4c20c797edaab7aa79c72ca29a7fe4bfd009fc8b34ff6b5223e0000000049454e44ae426082');
INSERT INTO "users" VALUES ('nhero','BNS','Staff','nhero123',X'89504e470d0a1a0a0000000d494844520000012200000122010000000075c5e21b0000018349444154789ced994d6ec3201484e715f644ea017a147cb32a37c347c90dcc3212d174f120699245baa87f621e0b64d02731c263fb3116e2751b3ffe00014619659451466d9d92da3c308a880cb9cd0cabeaea828a24c909906f1600702449de53cbebea82cad5e34cd9eb8c3e066bebea8a1a0f4bafd82de51fc602b82273ae68d423154826004ca1e80cc9b2beae3d53d5f7a35add41e2c91700973bef6f55fd7b53baf7b76081e3d75980701f356c55fd7b53d052324e4e3b72baceb1e815d356d5ef830a6701422ded81ecc1a378c8b0b2ae3d53cdd900d4f2299088fa2ca01ebaccf7b35075ef39015aec505f3c8e5ae7d8de2f445d8fb443eb98e65db16baaf9be35fdc2a65060be5f86bae59835cfc91e182dcf9997bad693ed55afe7dad02c6f35e6fc54cb3165400d33793c5c2cbf5f926282abe5651d6e43d71ea9a71c339e7c91980889132831ada3ab07aaed7d20800c102820f2670170f15c4b570f147eff1a84a3767182d598b3534f3966ed08d45bb18e2ea38c32ca28a3fe97fa01d6f9f154677734310000000049454e44ae426082');
INSERT INTO "users" VALUES ('sibayan','BHW','Staff','sibayan123',X'89504e470d0a1a0a0000000d494844520000012200000122010000000075c5e21b0000017f49444154789cedd93b8e83301485e1ff8e91521a691690a5982dcf0e6047b88c043a5360f252a44991c48cb19b48f0493e85b1ef754cfc3d86af2710545555555555b575656934985903c4f5499735d72e5490248da0de4f58879324e9567d3e57d1aa49bfb185f00306868860e0a66cb9f6a8d403d67d70c6aa2ec34fcfa857ceb857b5ee395e90769af4e8bae9da6afa22d46066662d104627605eca9cdcb98a56cb22bfac71c144fa0c72e6da8fb22ea6aa1e00f5cc06b1c1baacb976a186e384757ec2ac9d8dc10e7aa03e9f6b074a7db465a1a7d5ee4f6b4b9b3557d98a4bfbaade4f809f508fd3526d0649eab79abe081546807810614cbd95fa0de42a5a9deb1c411040fc5e3e030be39c2fd71e14d7576638014ed2e8045eaa7bcefbd5fd3da63f592a34f3e62a5adddf63124610b1c5f04e962bd73e55346368dd72eaa603770bb9ca57666b97b5fc79d56d245789eafe1e53c4060d9da1e1783e83b79afe7fab0775cecd8b5ae7bc4f3db8c7bc1e7afd8c555555555555e550bf41b9a360dbd83e0e0000000049454e44ae426082');
INSERT INTO "users" VALUES ('admin2','BNS','Admin','admin2',X'89504e470d0a1a0a0000000d494844520000012200000122010000000075c5e21b0000016249444154789ced9a4d8e83300c853f4fba871bf42870f47094b9012c2b815e17246da61a696613a0c559207e3e8927cb79b20d26fe5ec3d73f2070ca29a79c72eae894a5750158ccfa29dfe977d5750aaa93248d60d606014192a49fd4f6ba4e414d39c7bb6f3300f236d85797534ed5a02e2fd762aafc46a7f2cab16f046bd81b610065d37554f51f410d6666d682f5532e76cc92f31f5efd9b526bde17393e5c6f96b6c19ebace40b19692a9c60ceb1910a4989f2a1e55fd7b5329f63433e94010dd5816f91efb3a14650b054823283612dde8795f957a78ce8ca4196854b4b41efb8ad4c37324c56c37d218a4d8cc69d8e0b1af4295754e27606831200004d95ebace433de79839f91783c94c71575d9f4dbdd698d2084f0b72bfdf807acc31594b9cc5e874f3be765b6a4a231eeb093ebfdf941aae338ad385722f1c40d70752bff8fdf39395fbfd165431c764318616dcef6b53e6ff4639e594534e9d82ba03751bebd340bf24ae0000000049454e44ae426082');
COMMIT;
