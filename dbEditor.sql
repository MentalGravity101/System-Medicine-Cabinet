CREATE TABLE IF NOT EXISTS medicine_inventory (
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    date_stored DATE NOT NULL,
    expiration_date DATE
);

-- INSERT INTO medicine_inventory (name, type, quantity, unit, date_stored, expiration_date)
-- VALUES ('Biogesic', 'Paracetamol', 15, 'capsule', '2023-1-21', '2024-12-12');

-- INSERT INTO medicine_inventory (name, type, quantity, unit, date_stored, expiration_date)
-- VALUES ('Biogesic', 'Paracetamol', 15, 'capsule', '2024-1-21', '2024-10-12');

-- SELECT * FROM medicine_inventory;

CREATE TABLE IF NOT EXISTS door_logs (
    username TEXT NOT NULL,
    accountType TEXT NOT NULL,
    position TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    action_taken TEXT NOT NULL
);

-- INSERT INTO door_logs VALUES ('admin1', 'admin', 'BHW', '2024-1-21', '09:15:01', 'UNLOCK');
-- INSERT INTO door_logs VALUES ('admin1', 'admin', 'BHW', '2024-1-21', '09:20:30', 'LOCK');
-- INSERT INTO door_logs VALUES ('staff4', 'admin', 'BNS', '2024-5-16', '14:30:00', 'UNLOCK');
-- INSERT INTO door_logs VALUES ('staff4', 'admin', 'BNS', '2024-5-16', '15:00:00', 'LOCK');
-- INSERT INTO door_logs VALUES ('staff1', 'admin', 'Midwife', '2025-11-22', '03:51:09', 'UNLOCK');
-- INSERT INTO door_logs VALUES ('staff1', 'admin', 'Midwife', '2025-11-22', '03:57:23', 'LOCK');

INSERT INTO door_logs VALUES ('admin2', 'admin', 'Midwife', '2024-02-14', '10:05:15', 'UNLOCK');
INSERT INTO door_logs VALUES ('admin2', 'admin', 'Midwife', '2024-02-14', '10:10:45', 'LOCK');
INSERT INTO door_logs VALUES ('staff2', 'staff', 'BNS', '2024-03-03', '11:25:33', 'UNLOCK');
INSERT INTO door_logs VALUES ('staff2', 'staff', 'BNS', '2024-03-03', '11:35:01', 'LOCK');
INSERT INTO door_logs VALUES ('admin3', 'admin', 'BHW', '2024-07-21', '08:50:12', 'UNLOCK');
INSERT INTO door_logs VALUES ('admin3', 'admin', 'BHW', '2024-07-21', '09:00:45', 'LOCK');
INSERT INTO door_logs VALUES ('staff3', 'staff', 'Midwife', '2025-01-15', '07:22:50', 'UNLOCK');
INSERT INTO door_logs VALUES ('staff3', 'staff', 'Midwife', '2025-01-15', '07:30:23', 'LOCK');
INSERT INTO door_logs VALUES ('admin4', 'admin', 'BNS', '2025-04-30', '12:45:30', 'UNLOCK');
INSERT INTO door_logs VALUES ('admin4', 'admin', 'BNS', '2025-04-30', '12:55:10', 'LOCK');
INSERT INTO door_logs VALUES ('staff5', 'staff', 'BHW', '2025-08-09', '16:40:00', 'UNLOCK');
INSERT INTO door_logs VALUES ('staff5', 'staff', 'BHW', '2025-08-09', '16:50:30', 'LOCK');
INSERT INTO door_logs VALUES ('admin5', 'admin', 'Midwife', '2025-10-11', '13:15:15', 'UNLOCK');
INSERT INTO door_logs VALUES ('admin5', 'admin', 'Midwife', '2025-10-11', '13:25:55', 'LOCK');
INSERT INTO door_logs VALUES ('staff6', 'staff', 'BNS', '2026-02-28', '18:05:45', 'UNLOCK');
INSERT INTO door_logs VALUES ('staff6', 'staff', 'BNS', '2026-02-28', '18:12:33', 'LOCK');
INSERT INTO door_logs VALUES ('admin6', 'admin', 'BHW', '2026-05-16', '14:35:09', 'UNLOCK');
INSERT INTO door_logs VALUES ('admin6', 'admin', 'BHW', '2026-05-16', '14:45:48', 'LOCK');
INSERT INTO door_logs VALUES ('staff7', 'staff', 'Midwife', '2026-11-20', '09:50:27', 'UNLOCK');
INSERT INTO door_logs VALUES ('staff7', 'staff', 'Midwife', '2026-11-20', '10:00:00', 'LOCK');


SELECT * FROM door_logs;