CREATE DATABASE  IF NOT EXISTS `berrybot` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `berrybot`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: berrybot
-- ------------------------------------------------------
-- Server version	8.0.37

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `banidos`
--

DROP TABLE IF EXISTS `banidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banidos` (
  `telegram_id` bigint NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `data` date DEFAULT (curdate()),
  `adm` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`telegram_id`),
  KEY `fk_banidos_adm` (`adm`),
  CONSTRAINT `fk_banidos_adm` FOREIGN KEY (`adm`) REFERENCES `usuarios` (`username`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `banidos`
--

LOCK TABLES `banidos` WRITE;
/*!40000 ALTER TABLE `banidos` DISABLE KEYS */;
/*!40000 ALTER TABLE `banidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cartas`
--

DROP TABLE IF EXISTS `cartas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cartas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `raridade` int NOT NULL,
  `imagem` varchar(300) NOT NULL,
  `categoria` varchar(100) NOT NULL,
  `subcategoria` varchar(100) NOT NULL,
  `tag` varchar(255) DEFAULT NULL,
  `deletehash` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cartas_ibfk_1` (`categoria`,`subcategoria`),
  KEY `fk_cartas_tag` (`tag`),
  CONSTRAINT `cartas_ibfk_1` FOREIGN KEY (`categoria`, `subcategoria`) REFERENCES `divisoes` (`categoria`, `subcategoria`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cartas_tag` FOREIGN KEY (`tag`) REFERENCES `tags` (`nome`) ON UPDATE CASCADE,
  CONSTRAINT `cartas_chk_1` CHECK ((`raridade` in (1,2,3)))
) ENGINE=InnoDB AUTO_INCREMENT=1193 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cartas`
--

LOCK TABLES `cartas` WRITE;
/*!40000 ALTER TABLE `cartas` DISABLE KEYS */;
INSERT INTO `cartas` VALUES (1001,'Hyunjin',1,'https://i.imgur.com/7DsR8Ur.jpeg','ASIAFARM','Stray Kids',NULL,'2HtP7VhgE1AYWmO'),(1002,'Bang Chan',1,'https://i.imgur.com/oz1o3Of.jpeg','ASIAFARM','Stray Kids',NULL,'XDdYyqchDd5yEj1'),(1003,'Felix',1,'https://i.imgur.com/TDLQCOA.jpeg','ASIAFARM','Stray Kids',NULL,'MWjdo11OUmdX5nE'),(1004,'Han',2,'https://i.imgur.com/fnqBljX.jpeg','ASIAFARM','Stray Kids',NULL,'pfF7GSm4WMhK9Lr'),(1005,'Changbin',2,'https://i.imgur.com/QXh2HtD.jpeg','ASIAFARM','Stray Kids',NULL,'c41FKSqkpx79ODP'),(1006,'Lee Know',2,'https://i.imgur.com/Mf9MYvD.jpeg','ASIAFARM','Stray Kids',NULL,'rvRRhrxj9GUp9nP'),(1007,'I.N',2,'https://i.imgur.com/6CWDwCf.jpeg','ASIAFARM','Stray Kids',NULL,'jXFtZVwv5vfkO9X'),(1008,'Seungmin',2,'https://i.imgur.com/4jCvJ7s.jpeg','ASIAFARM','Stray Kids',NULL,'bUNwEkzGZPEcYQL'),(1009,'Wumuti',2,'https://i.imgur.com/K9hHUMj.jpeg','ASIAFARM','XLOV',NULL,'6YpDs5vd4coSvA8'),(1010,'Rui',2,'https://i.imgur.com/l5pCsUT.jpeg','ASIAFARM','XLOV',NULL,'xCCsSlkUK0a17Yu'),(1011,'Hyun',2,'https://i.imgur.com/CFNzwrC.jpeg','ASIAFARM','XLOV',NULL,'aUGTnjH1iP4oaG1'),(1012,'Haru',2,'https://i.imgur.com/aECRcd9.jpeg','ASIAFARM','XLOV',NULL,'cOGh0LgdD7nmG31'),(1013,'Sion',1,'https://i.imgur.com/I06m07J.jpeg','ASIAFARM','NCT Wish',NULL,'8Pvlt0lWqsianuj'),(1014,'Riku',2,'https://i.imgur.com/epkFq5p.jpeg','ASIAFARM','NCT Wish',NULL,'luUZRFrcenNvyAN'),(1015,'Yushi',2,'https://i.imgur.com/2frK5qq.jpeg','ASIAFARM','NCT Wish',NULL,'Jv0tyB9uekAvhiv'),(1016,'Jaehee',2,'https://i.imgur.com/epA5xVs.jpeg','ASIAFARM','NCT Wish',NULL,'OC4Ds5MkC6eX3SW'),(1017,'Ryo',2,'https://i.imgur.com/YQ3zOD0.jpeg','ASIAFARM','NCT Wish',NULL,'uMQ6yAOz35jJp2H'),(1018,'Sakuya',1,'https://i.imgur.com/yzFHcBh.jpeg','ASIAFARM','NCT Wish',NULL,'rFsiEGKUB2J4zeC'),(1019,'Hanbin',1,'https://i.imgur.com/03oYIHU.jpeg','ASIAFARM','ZEROBASEONE',NULL,'S7UVsUB4YzpXndI'),(1020,'Zhang Hao',1,'https://i.imgur.com/XugmoHJ.jpeg','ASIAFARM','ZEROBASEONE',NULL,'Raj0t5v5quO8xQC'),(1021,'Ricky',1,'https://i.imgur.com/S4m83AY.jpeg','ASIAFARM','ZEROBASEONE',NULL,'EhiDa0X0qpgp7de'),(1022,'Jiwoong',2,'https://i.imgur.com/oeoH3xT.jpeg','ASIAFARM','ZEROBASEONE',NULL,'vFNW9D8tXcwiOMI'),(1023,'Matthew',2,'https://i.imgur.com/VEYsMVW.jpeg','ASIAFARM','ZEROBASEONE',NULL,'G1qIUiPmplutl2M'),(1024,'Taerae',2,'https://i.imgur.com/5XNEhkw.jpeg','ASIAFARM','ZEROBASEONE',NULL,'AIBJs1CPBUjT1eS'),(1025,'Gyuvin',2,'https://i.imgur.com/OhHHSXl.jpeg','ASIAFARM','ZEROBASEONE',NULL,'RNhYV9Cq6HZlyPP'),(1026,'Gunwook',2,'https://i.imgur.com/hulDPH8.jpeg','ASIAFARM','ZEROBASEONE',NULL,'2qCdzgbpUJtxtO8'),(1027,'Yujin',2,'https://i.imgur.com/Nz5lIHg.jpeg','ASIAFARM','ZEROBASEONE',NULL,'REMLyTBRgETO7fS'),(1028,'Chaewon',1,'https://i.imgur.com/qDYvyoB.jpeg','ASIAFARM','LE SSERAFIM',NULL,'xd2KCrj0JlduO2v'),(1029,'Yunjin',1,'https://i.imgur.com/MYKtP18.jpeg','ASIAFARM','LE SSERAFIM',NULL,'zXbswJCh3MUDMvC'),(1030,'Sakura',2,'https://i.imgur.com/eGdc64G.jpeg','ASIAFARM','LE SSERAFIM',NULL,'BpIQcmxWeNo0RHS'),(1031,'Kazuha',2,'https://i.imgur.com/shyCaQ2.jpeg','ASIAFARM','LE SSERAFIM',NULL,'pHZZ5yHpVt0pLf9'),(1032,'Eunchae',2,'https://i.imgur.com/ak5BwAK.jpeg','ASIAFARM','LE SSERAFIM',NULL,'yuJ7jzaY1lFjOKh'),(1033,'Keeho',1,'https://i.imgur.com/Dr0zc6t.jpeg','ASIAFARM','P1Harmony',NULL,'S4be6WrqgGo7mpB'),(1034,'Intak',1,'https://i.imgur.com/LvQgQtU.jpeg','ASIAFARM','P1Harmony',NULL,'dSdEOcriMBIzZwg'),(1035,'Theo',2,'https://i.imgur.com/05xqvRF.jpeg','ASIAFARM','P1Harmony',NULL,'DhWRJSKRavtOlwz'),(1036,'Jiung',2,'https://i.imgur.com/E0XtujU.jpeg','ASIAFARM','P1Harmony',NULL,'I0x4tGuutPJFN0p'),(1037,'Soul',2,'https://i.imgur.com/vQGL6hU.jpeg','ASIAFARM','P1Harmony',NULL,'syjutAiictw27c1'),(1038,'Jongseob',2,'https://i.imgur.com/hrSrc5l.jpeg','ASIAFARM','P1Harmony',NULL,'pWjEjJHS56YHxng'),(1039,'Suga',1,'https://i.imgur.com/5n1e3RF.jpeg','ASIAFARM','BTS',NULL,'X8QtCZMxkVgk15o'),(1040,'V',1,'https://i.imgur.com/SAUDMXt.jpeg','ASIAFARM','BTS',NULL,'hNyqnR1nwuS4pk8'),(1041,'Jungkook',1,'https://i.imgur.com/l8qcuED.jpeg','ASIAFARM','BTS',NULL,'rV2xG4olMJbbQ4J'),(1042,'Jin',2,'https://i.imgur.com/dvLOfvH.jpeg','ASIAFARM','BTS',NULL,'c1vHU8b1EfA7keR'),(1043,'RM',2,'https://i.imgur.com/hAEeeiA.jpeg','ASIAFARM','BTS',NULL,'kOdnFgdOWs6fdmb'),(1044,'J-Hope',2,'https://i.imgur.com/9Z6l4nq.jpeg','ASIAFARM','BTS',NULL,'F5CK2U9YzHQYZsB'),(1045,'Jimin',2,'https://i.imgur.com/qD9JrxM.jpeg','ASIAFARM','BTS',NULL,'G6JxwvahsOTjT8T'),(1046,'Jennie',1,'https://i.imgur.com/hyliFnc.jpeg','ASIAFARM','BLACKPINK',NULL,'joZxDDENV1t8oIc'),(1047,'Jisoo',2,'https://i.imgur.com/ShKUwwD.jpeg','ASIAFARM','BLACKPINK',NULL,'ZBh14PvQXcTvar9'),(1048,'Rosé',2,'https://i.imgur.com/OiW81md.jpeg','ASIAFARM','BLACKPINK',NULL,'kNRijX0Hqs1wJmi'),(1049,'Lisa',2,'https://i.imgur.com/iuyIqmd.jpeg','ASIAFARM','BLACKPINK',NULL,'hklNNxAvzkqkQpX'),(1050,'Minwook',1,'https://i.imgur.com/q1ueNB8.jpeg','ASIAFARM','CYE',NULL,'TYXeXfM3MVOl1WY'),(1051,'Ma Jingxiang',1,'https://i.imgur.com/6xz1t39.jpeg','ASIAFARM','CYE',NULL,'jkrJyMVI48q7Njz'),(1052,'Kenshin',1,'https://i.imgur.com/LIYBElN.jpeg','ASIAFARM','CYE',NULL,'dRDKKaLFaKm7TUt'),(1053,'Yeojun',2,'https://i.imgur.com/RnBM32f.jpeg','ASIAFARM','CYE',NULL,'Im8fxd9rxbDOA8K'),(1054,'Sungmin',2,'https://i.imgur.com/MUzj9EV.jpeg','ASIAFARM','CYE',NULL,'HMOtHWWpGezqp0X'),(1055,'Seungho',2,'https://i.imgur.com/Upzjf4y.jpeg','ASIAFARM','CYE',NULL,'PxYXOoe9KxVV0Fy'),(1056,'Kyoungbae',2,'https://i.imgur.com/FxxRpNB.jpeg','ASIAFARM','CYE',NULL,'YqWDMJXiAMyt9zf'),(1057,'Wonyoung',1,'https://i.imgur.com/8SkiZ08.jpeg','ASIAFARM','IVE',NULL,'Pjh2zMdzULxjENg'),(1058,'Yujin',1,'https://i.imgur.com/Phf1ZLv.jpeg','ASIAFARM','IVE',NULL,'L4GevPuTcoQTCK5'),(1059,'Leeseo',2,'https://i.imgur.com/P5OtCQA.jpeg','ASIAFARM','IVE',NULL,'p6NLZfqDq8ytGoZ'),(1060,'Gaeul',2,'https://i.imgur.com/pepQ1oy.jpeg','ASIAFARM','IVE',NULL,'Kgd3CF1f81kBYew'),(1061,'Rei',2,'https://i.imgur.com/rMFxePv.jpeg','ASIAFARM','IVE',NULL,'1QB8D1JXoZu2XeV'),(1062,'Liz',2,'https://i.imgur.com/ROkxkKo.jpeg','ASIAFARM','IVE',NULL,'vLXEt6vNAO7JzLx'),(1063,'Mark',1,'https://i.imgur.com/lZh8R7V.jpeg','ASIAFARM','NCT Dream',NULL,'gvPeIRYTbH1vYUy'),(1064,'Haechan',1,'https://i.imgur.com/xTPEdvL.jpeg','ASIAFARM','NCT Dream',NULL,'1q4FKKbZavNmDLF'),(1065,'Jaemin',1,'https://i.imgur.com/Pn6eTOA.jpeg','ASIAFARM','NCT Dream',NULL,'kPInVnnAcgr5hSs'),(1066,'Jeno',2,'https://i.imgur.com/9MyMkEd.jpeg','ASIAFARM','NCT Dream',NULL,'lwdtgVe7zkxFuBl'),(1067,'Jisung',2,'https://i.imgur.com/3Tu3Lry.jpeg','ASIAFARM','NCT Dream',NULL,'7iArOvAQmmE4pYd'),(1068,'Chenle',2,'https://i.imgur.com/Am6DUCg.jpeg','ASIAFARM','NCT Dream',NULL,'VS8fmTOClo4mhdP'),(1069,'Renjun',2,'https://i.imgur.com/oSqzFs8.jpeg','ASIAFARM','NCT Dream',NULL,'Kt6McGJDnRrxl6s'),(1070,'Ten',1,'https://i.imgur.com/OZmAJjo.jpeg','ASIAFARM','WayV',NULL,'FW5EonqBl2MdYrR'),(1071,'Xiaojun',1,'https://i.imgur.com/yZaQKR3.jpeg','ASIAFARM','WayV',NULL,'dNkHls2mA2cSR8t'),(1072,'Kun',2,'https://i.imgur.com/6DHH9ON.jpeg','ASIAFARM','WayV',NULL,'AEWwdHdCciAr359'),(1073,'Winwin',2,'https://i.imgur.com/OF5eyoD.jpeg','ASIAFARM','WayV',NULL,'M8KACAGXR1jL2Ud'),(1074,'Hendery',2,'https://i.imgur.com/Xci89eN.jpeg','ASIAFARM','WayV',NULL,'u1i67UxNxZWYiwk'),(1075,'Yangyang',2,'https://i.imgur.com/1SkpJhg.jpeg','ASIAFARM','WayV',NULL,'thaFM6DszSknjFx'),(1076,'Taeyong',1,'https://i.imgur.com/Hj8MiZy.jpeg','ASIAFARM','NCT 127',NULL,'LUo5Eo2t47oYWfY'),(1077,'Jaehyun',1,'https://i.imgur.com/W2JwRGh.jpeg','ASIAFARM','NCT 127',NULL,'McSFobEWvE3kbG5'),(1078,'Johnny',2,'https://i.imgur.com/TAfVawu.jpeg','ASIAFARM','NCT 127',NULL,'3joeLi977pYbHCA'),(1079,'Yuta',2,'https://i.imgur.com/LlaczQY.jpeg','ASIAFARM','NCT 127',NULL,'qElW6NoTGBQbshi'),(1080,'Doyoung',2,'https://i.imgur.com/Obra3I5.jpeg','ASIAFARM','NCT 127',NULL,'eaa66z3xx7v0jIx'),(1081,'Jungwoo',2,'https://i.imgur.com/laQAwBY.jpeg','ASIAFARM','NCT 127',NULL,'EwQckxTxguSoZRd'),(1082,'Giselle',1,'https://i.imgur.com/3Y7nSRq.jpeg','ASIAFARM','aespa',NULL,'ydS14kXbafmB60M'),(1083,'Winter',1,'https://i.imgur.com/diKMTPQ.jpeg','ASIAFARM','aespa',NULL,'6vi0z95jTQNxemt'),(1084,'Karina',2,'https://i.imgur.com/bfLWfvJ.jpeg','ASIAFARM','aespa',NULL,'GzEoaAh5aMWVAUw'),(1085,'Ningning',2,'https://i.imgur.com/cFGemlL.jpeg','ASIAFARM','aespa',NULL,'ymvSFYEqGXlUuzz'),(1086,'Jiyu',1,'https://i.imgur.com/epvNA5W.jpeg','ASIAFARM','KIIIKIII',NULL,'SXM3LPhqbNbbjMQ'),(1087,'Haum',1,'https://i.imgur.com/y54HQNl.jpeg','ASIAFARM','KIIIKIII',NULL,'9URpELnha747jSi'),(1088,'Leesol',2,'https://i.imgur.com/w0gWIW8.jpeg','ASIAFARM','KIIIKIII',NULL,'wUOC560fhqC8ipq'),(1089,'Sui',2,'https://i.imgur.com/IERUuNr.jpeg','ASIAFARM','KIIIKIII',NULL,'UvgfyJOUNhBKssl'),(1090,'Kya',2,'https://i.imgur.com/6whyJga.jpeg','ASIAFARM','KIIIKIII',NULL,'LDtXhOBjgWqS7kL'),(1091,'Sophia',1,'https://i.imgur.com/sFEDEb1.jpeg','ASIAFARM','KATSEYE',NULL,'HjRNAC7mXNZ72bp'),(1092,'Daniela',1,'https://i.imgur.com/clL2UkW.jpeg','ASIAFARM','KATSEYE',NULL,'RwcYjJAhTgWqgs8'),(1093,'Lara',1,'https://i.imgur.com/4AxJxxX.jpeg','ASIAFARM','KATSEYE',NULL,'Ls5z3XSvxQPitkK'),(1094,'Manon',2,'https://i.imgur.com/RhWU3Yp.jpeg','ASIAFARM','KATSEYE',NULL,'6nQP9vjzU3OeFR1'),(1095,'Megan',2,'https://i.imgur.com/tLuAIcV.jpeg','ASIAFARM','KATSEYE',NULL,'5zKU1eMziebmhUY'),(1096,'Yoonchae',2,'https://i.imgur.com/wGS6onD.jpeg','ASIAFARM','KATSEYE',NULL,'zS8YmYjyVmVbbuf'),(1098,'Minji',1,'https://i.imgur.com/6GoceSv.jpeg','ASIAFARM','NJZ',NULL,'LdXu02QKSaMYIFl'),(1099,'Hanni',1,'https://i.imgur.com/Gs6wrc4.jpeg','ASIAFARM','NJZ',NULL,'BGprKlp867jacTO'),(1100,'Danielle',2,'https://i.imgur.com/VDCYjiY.jpeg','ASIAFARM','NJZ',NULL,'HvMcgbWOlGUv99k'),(1101,'Haerin',2,'https://i.imgur.com/zuKgnyp.jpeg','ASIAFARM','NJZ',NULL,'XSgzWtJU8AarDRY'),(1102,'Hyein',2,'https://i.imgur.com/ljCVIy9.jpeg','ASIAFARM','NJZ',NULL,'QgibVeUPH59OXP7'),(1103,'Irene',1,'https://i.imgur.com/wgkBRng.jpeg','ASIAFARM','Red Velvet',NULL,'5qpfiFczntVLB1z'),(1104,'Seulgi',1,'https://i.imgur.com/Ks6N4KP.jpeg','ASIAFARM','Red Velvet',NULL,'6rmpt4C5LbTsLRk'),(1105,'Wendy',2,'https://i.imgur.com/A8VZRzy.jpeg','ASIAFARM','Red Velvet',NULL,'PBGo05If8RoNxix'),(1106,'Joy',2,'https://i.imgur.com/oIrM9uc.jpeg','ASIAFARM','Red Velvet',NULL,'lTfgcMhLcwL6hES'),(1107,'Yeri',2,'https://i.imgur.com/6jzY5Ua.jpeg','ASIAFARM','Red Velvet',NULL,'EGT8sj9lyJgGSXr'),(1108,'Moka',1,'https://i.imgur.com/xYqpGwt.jpeg','ASIAFARM','ILLIT',NULL,'zEKoxNJ5UyTRTIr'),(1109,'Wonhee',1,'https://i.imgur.com/hu4vTgc.jpeg','ASIAFARM','ILLIT',NULL,'yEBVkQJ214FxvOo'),(1110,'Yunah',2,'https://i.imgur.com/OTDU9tx.jpeg','ASIAFARM','ILLIT',NULL,'gJOoqhHNcTWxLHQ'),(1111,'Minju',2,'https://i.imgur.com/LgpPNXI.jpeg','ASIAFARM','ILLIT',NULL,'CB4d1MbFsNDFtQE'),(1112,'Iroha',2,'https://i.imgur.com/kPA6iHN.jpeg','ASIAFARM','ILLIT',NULL,'Gwy6Yup0TnPACCX'),(1113,'Jaehyun',1,'https://i.imgur.com/zPUUEY3.jpeg','ASIAFARM','BOYNEXTDOOR',NULL,'FFs14OfQYv8MNaE'),(1114,'Taesan',1,'https://i.imgur.com/hVSrg9P.jpeg','ASIAFARM','BOYNEXTDOOR',NULL,'hd5PcSne3Ckbaln'),(1115,'Sungho',2,'https://i.imgur.com/tWX8RCS.jpeg','ASIAFARM','BOYNEXTDOOR',NULL,'JZQOghsJzhmm1tG'),(1116,'Riwoo',2,'https://i.imgur.com/s0KWbYX.jpeg','ASIAFARM','BOYNEXTDOOR',NULL,'o0x5Xa8ZPydef9Z'),(1117,'Leehan',2,'https://i.imgur.com/IkgOxb1.jpeg','ASIAFARM','BOYNEXTDOOR',NULL,'8vGdmBARYQflxLz'),(1118,'Woonhak',2,'https://i.imgur.com/Mi0sN3V.jpeg','ASIAFARM','BOYNEXTDOOR',NULL,'kW1jcGxl7pcb4Ly'),(1119,'Nayeon',1,'https://i.imgur.com/sUna7my.jpeg','ASIAFARM','TWICE',NULL,'clDcmPtCH89tzju'),(1120,'Mina',1,'https://i.imgur.com/bynTCw2.jpeg','ASIAFARM','TWICE',NULL,'Wn7LVNdyTs2b9wU'),(1121,'Momo',1,'https://i.imgur.com/BOvnRsE.jpeg','ASIAFARM','TWICE',NULL,'bZQDqaOJTDXz4mR'),(1122,'Sana',1,'https://i.imgur.com/Vk12Pi0.jpeg','ASIAFARM','TWICE',NULL,'abzKmj6dZV47BFe'),(1123,'Jihyo',2,'https://i.imgur.com/U7bMyqx.jpeg','ASIAFARM','TWICE',NULL,'E5TvsHi3fbFaHTK'),(1124,'Tzuyu',2,'https://i.imgur.com/tzuXUHY.jpeg','ASIAFARM','TWICE',NULL,'Ejkizjh1J9Ab3qb'),(1125,'Jeongyeon',2,'https://i.imgur.com/8oiM6Yy.jpeg','ASIAFARM','TWICE',NULL,'Ody99Kj4sLglSyX'),(1126,'Dahyun',2,'https://i.imgur.com/0MbFvba.jpeg','ASIAFARM','TWICE',NULL,'moFO4fsF89sJ7Md'),(1127,'Chaeyoung',2,'https://i.imgur.com/UZN135T.jpeg','ASIAFARM','TWICE',NULL,'VejPeX9tFCW4z86'),(1128,'Yeji',1,'https://i.imgur.com/DXsUrjY.jpeg','ASIAFARM','ITZY',NULL,'iw043fMHlDzpy2l'),(1129,'Chaeryeong',1,'https://i.imgur.com/v7JCvgp.jpeg','ASIAFARM','ITZY',NULL,'kim0uhAfveFIKVc'),(1130,'Lia',2,'https://i.imgur.com/OfYlia8.jpeg','ASIAFARM','ITZY',NULL,'X066U03PG2fiTXw'),(1131,'Ryujin',2,'https://i.imgur.com/v6zNg0f.jpeg','ASIAFARM','ITZY',NULL,'8C9sr8taIYGfwkt'),(1132,'Yuna',2,'https://i.imgur.com/ZSEsTun.jpeg','ASIAFARM','ITZY',NULL,'3VtYbsZRSIMCYm3'),(1133,'Jeonghan',1,'https://i.imgur.com/HsVV88M.jpeg','ASIAFARM','SEVENTEEN',NULL,'NVYGlNqa75LnZGg'),(1134,'Joshua',1,'https://i.imgur.com/7UbgLNF.jpeg','ASIAFARM','SEVENTEEN',NULL,'Pwm6m5APsOGhBtE'),(1135,'Hoshi',1,'https://i.imgur.com/nKRfAaA.jpeg','ASIAFARM','SEVENTEEN',NULL,'VRiirXAUtJ1smzv'),(1136,'Wonwoo',1,'https://i.imgur.com/AgkRHye.jpeg','ASIAFARM','SEVENTEEN',NULL,'Nb02EO1BI7Ll8jK'),(1137,'DK',1,'https://i.imgur.com/kbLwtTK.jpeg','ASIAFARM','SEVENTEEN',NULL,'Y6IIeSgkceiETBO'),(1138,'Mingyu',1,'https://i.imgur.com/ehNhKVp.jpeg','ASIAFARM','SEVENTEEN',NULL,'F79jtSh7XjpjSWU'),(1139,'S.coups',2,'https://i.imgur.com/n8KpycX.jpeg','ASIAFARM','SEVENTEEN',NULL,'ccdplnVC5RpbV4B'),(1140,'Jun',2,'https://i.imgur.com/2VjPqYy.jpeg','ASIAFARM','SEVENTEEN',NULL,'jxISZcpp0doZLUS'),(1141,'Woozi',2,'https://i.imgur.com/qNH84M0.jpeg','ASIAFARM','SEVENTEEN',NULL,'9CJtKgnFa3jsL5u'),(1142,'The8',2,'https://i.imgur.com/fvgzw0v.jpeg','ASIAFARM','SEVENTEEN',NULL,'344hiJY6AJBU06U'),(1143,'Seungkwan',2,'https://i.imgur.com/9AC93ER.jpeg','ASIAFARM','SEVENTEEN',NULL,'Tr3n0QYj0eYAteI'),(1144,'Vernon',2,'https://i.imgur.com/u0BiJmH.jpeg','ASIAFARM','SEVENTEEN',NULL,'7F700NSGejkmm6x'),(1145,'Dino',2,'https://i.imgur.com/5IhCrzV.jpeg','ASIAFARM','SEVENTEEN',NULL,'n1WdiGqvES3JKwg'),(1146,'Jeemin',1,'https://i.imgur.com/f4zg6aO.jpeg','ASIAFARM','izna',NULL,'I4rAVyardGhl9qm'),(1147,'Jiyoon',1,'https://i.imgur.com/f2aHD4c.jpeg','ASIAFARM','izna',NULL,'MIsCkmb41vPoYgS'),(1148,'Jungeun',1,'https://i.imgur.com/o8yomv6.jpeg','ASIAFARM','izna',NULL,'UMKA9Diy81o5tcA'),(1149,'Mai',2,'https://i.imgur.com/2FqPmER.jpeg','ASIAFARM','izna',NULL,'NbUW5edBCewsF2S'),(1150,'Koko',2,'https://i.imgur.com/noNJpAK.jpeg','ASIAFARM','izna',NULL,'ze7FVKLmG3NVi9T'),(1151,'Sarang',2,'https://i.imgur.com/woEcJw5.jpeg','ASIAFARM','izna',NULL,'B8422JB4aR832Zv'),(1152,'Saebi',2,'https://i.imgur.com/1ZqQxzk.jpeg','ASIAFARM','izna',NULL,'qn7G8BlwdYnUbsm'),(1153,'Heeseung',1,'https://i.imgur.com/CijFPJT.jpeg','ASIAFARM','ENHYPEN',NULL,'LZLOrrUzVd11ALV'),(1154,'Sunghoon',1,'https://i.imgur.com/3qdpES1.jpeg','ASIAFARM','ENHYPEN',NULL,'ecSZsFxsXIl8EZK'),(1155,'Sunoo',1,'https://i.imgur.com/oKgJXB7.jpeg','ASIAFARM','ENHYPEN',NULL,'FvDle2axDgIm6df'),(1156,'Jay',2,'https://i.imgur.com/UDQR9DJ.jpeg','ASIAFARM','ENHYPEN',NULL,'yGRSRiWhlrXGu4z'),(1157,'Jake',2,'https://i.imgur.com/6Ka4B8V.jpeg','ASIAFARM','ENHYPEN',NULL,'Yt83vnfkX5BeePU'),(1158,'Jungwon',2,'https://i.imgur.com/SwmoOnp.jpeg','ASIAFARM','ENHYPEN',NULL,'1Fu14srB51eEIHJ'),(1159,'Ni-ki',2,'https://i.imgur.com/XEYYBBU.jpeg','ASIAFARM','ENHYPEN',NULL,'Xyx2d4hBfm6yQWt'),(1161,'Seonghwa',1,'https://i.imgur.com/zt4EPc1.jpeg','ASIAFARM','ATEEZ',NULL,'9Ai7oUoiDs7bCPY'),(1162,'San',1,'https://i.imgur.com/8QGuY5k.jpeg','ASIAFARM','ATEEZ',NULL,'MAxXi2RfF8UhjJf'),(1163,'Mingi',1,'https://i.imgur.com/6pV81w5.jpeg','ASIAFARM','ATEEZ',NULL,'4YTTfQTj6qfPYMi'),(1164,'Hongjoong',2,'https://i.imgur.com/nTrNBW9.jpeg','ASIAFARM','ATEEZ',NULL,'r0vfQPfpBphfGOs'),(1165,'Yunho',2,'https://i.imgur.com/2I47jEG.jpeg','ASIAFARM','ATEEZ',NULL,'lzkt2kHxnD9Qobw'),(1166,'Yeosang',2,'https://i.imgur.com/okD3INd.jpeg','ASIAFARM','ATEEZ',NULL,'dNf3nDScU2oyfpD'),(1167,'Wooyoung',2,'https://i.imgur.com/FMQNlxy.jpeg','ASIAFARM','ATEEZ',NULL,'le05AY1bSArhudu'),(1168,'Jongho',2,'https://i.imgur.com/rTCISvN.jpeg','ASIAFARM','ATEEZ',NULL,'jTmtMQXXycVFBH1'),(1169,'K',1,'https://i.imgur.com/VjnudB1.jpeg','ASIAFARM','&TEAM',NULL,'IQ2nVIRz1VTymgK'),(1170,'Nicholas',1,'https://i.imgur.com/8iovXJR.jpeg','ASIAFARM','&TEAM',NULL,'rTyfe5PltGJ5wy3'),(1171,'Harua',1,'https://i.imgur.com/3Ss5OUt.jpeg','ASIAFARM','&TEAM',NULL,'OT2pOUOuoSoe4Ho'),(1172,'Maki',1,'https://i.imgur.com/m3nbziY.jpeg','ASIAFARM','&TEAM',NULL,'RxblcZrqW4tZP6u'),(1173,'Fuma',2,'https://i.imgur.com/tJQErFX.jpeg','ASIAFARM','&TEAM',NULL,'O6Osp1xD58ipWAY'),(1174,'EJ',2,'https://i.imgur.com/bxEtw9M.jpeg','ASIAFARM','&TEAM',NULL,'thTKrtMn0HCrwbM'),(1175,'Yuma',2,'https://i.imgur.com/7MENUyn.jpeg','ASIAFARM','&TEAM',NULL,'Zd00qSkObgjKSbY'),(1176,'Jo',2,'https://i.imgur.com/bOFQOgK.jpeg','ASIAFARM','&TEAM',NULL,'Ff9zB8QWDU86Rxw'),(1177,'Taki',2,'https://i.imgur.com/jiijAom.jpeg','ASIAFARM','&TEAM',NULL,'yfKQW2NRIkBM5ti'),(1178,'Soobin',1,'https://i.imgur.com/v6BzK6d.jpeg','ASIAFARM','TXT',NULL,'SBIoKQKEG0fB5cL'),(1179,'Yeonjun',1,'https://i.imgur.com/CqlJpeC.jpeg','ASIAFARM','TXT',NULL,'ZNJiHG036dTNeJ9'),(1180,'Beomgyu',2,'https://i.imgur.com/RqS5f8b.jpeg','ASIAFARM','TXT',NULL,'fpzbG3p43JXdCV3'),(1181,'Taehyun',2,'https://i.imgur.com/u2Pz7q5.jpeg','ASIAFARM','TXT',NULL,'KYOHTqVFJmlOwbG'),(1182,'Huening Kai',2,'https://i.imgur.com/VtOS8B1.jpeg','ASIAFARM','TXT',NULL,'iaP8Ag0ohBjaSkw');
/*!40000 ALTER TABLE `cartas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `divisoes`
--

DROP TABLE IF EXISTS `divisoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `divisoes` (
  `categoria` varchar(100) NOT NULL,
  `subcategoria` varchar(100) NOT NULL,
  `imagem` varchar(300) DEFAULT NULL,
  `shortner` varchar(200) DEFAULT NULL,
  `deletehash` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`categoria`,`subcategoria`),
  KEY `index_sub` (`subcategoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `divisoes`
--

LOCK TABLES `divisoes` WRITE;
/*!40000 ALTER TABLE `divisoes` DISABLE KEYS */;
INSERT INTO `divisoes` VALUES ('ASIAFARM','&TEAM','https://i.imgur.com/k5Se23F.jpeg','&t,teamies','WBxV9CbIM9z77hf'),('ASIAFARM','aespa','https://i.imgur.com/uECkiag.jpeg',NULL,'PmH6MP0NQR7rfss'),('ASIAFARM','ATEEZ','https://i.imgur.com/NYwi3mR.jpeg',NULL,'m2pTLxnHIw8cp7O'),('ASIAFARM','BLACKPINK','https://i.imgur.com/8WE6iHr.jpeg','bp','fPzgRdOJVMYTjQ5'),('ASIAFARM','BOYNEXTDOOR','https://i.imgur.com/bxeDrvR.jpeg','bnd,bonedo','jEtVUr9fGb1haVa'),('ASIAFARM','BTS','https://i.imgur.com/mvMWGsM.jpeg',NULL,'l43rB2f9NeHKBRp'),('ASIAFARM','CYE','https://i.imgur.com/PoD0L4I.jpeg',NULL,'m1H0HebLQm0aGrD'),('ASIAFARM','ENHYPEN','https://i.imgur.com/9Yub8fA.jpeg','enha,enhy','hL8zMTwan8NXsXc'),('ASIAFARM','ILLIT','https://i.imgur.com/R5SuP9c.jpeg',NULL,'INMfh8p572Qqz9c'),('ASIAFARM','ITZY','https://i.imgur.com/zW73wz5.jpeg',NULL,'cUJnjp1oQBCwHmt'),('ASIAFARM','IVE','https://i.imgur.com/aQTcJTx.jpeg',NULL,'5DHUENklQGzWnds'),('ASIAFARM','izna','https://i.imgur.com/lI3FjUN.jpeg',NULL,'T96MGfIR7uY0Ymq'),('ASIAFARM','KATSEYE','https://i.imgur.com/gVKwXig.jpeg',NULL,'1ZLQG4amS1rld5m'),('ASIAFARM','KIIIKIII','https://i.imgur.com/HkkZgk0.jpeg',NULL,'Ws4CT165IoQtmbC'),('ASIAFARM','LE SSERAFIM','https://i.imgur.com/hvPcLJR.jpeg','lsf,fimmies','HwKpd9M9zVnxS1W'),('ASIAFARM','NCT 127','https://i.imgur.com/RNZbr6w.jpeg','127','T8R8jLapEujr8Cv'),('ASIAFARM','NCT Dream','https://i.imgur.com/EaCgAil.jpeg','dream,nd','lskXnE44FKuY5L4'),('ASIAFARM','NCT Wish','https://i.imgur.com/9FigL5Y.jpeg','wish,nw','N9zxDUdZS83juZl'),('ASIAFARM','NJZ','https://i.imgur.com/X9jhL4v.jpeg','newjeans','qOZsZnAfuem2on8'),('ASIAFARM','P1Harmony','https://i.imgur.com/bDJneb7.jpeg','p1,p1h,piwon','tdusjHsJHzUL3Mw'),('ASIAFARM','Red Velvet','https://i.imgur.com/dljG5sj.jpeg','redvelvet,rv,reve','xt0pYVwMEnjtfpi'),('ASIAFARM','SEVENTEEN','https://i.imgur.com/M0oGO2U.jpeg','svt,17','d2JvgQyN54xbz27'),('ASIAFARM','Stray Kids','https://i.imgur.com/VArTdkL.jpeg','skz,143','I5m1OBo0f1jUgTf'),('ASIAFARM','TWICE','https://i.imgur.com/RQ5p2FL.jpeg',NULL,'oNTVpdE5OazJyge'),('ASIAFARM','TXT','https://i.imgur.com/n4uCBHW.jpeg',NULL,'isXxhszWvRHrdxJ'),('ASIAFARM','WayV','https://i.imgur.com/cjxy5ce.jpeg',NULL,'IvqLTHESikYYMaI'),('ASIAFARM','XG','https://i.imgur.com/UEGXyxX.jpeg',NULL,'xh9DuW1Tvwedj0U'),('ASIAFARM','XLOV','https://i.imgur.com/2uvOwQR.jpeg',NULL,'wf19MosJH6Z09Ft'),('ASIAFARM','ZEROBASEONE','https://i.imgur.com/O5S50Xk.jpeg','zb1,zerobaseconas,jbw,jebewon','DVXqfQNiejppsBa');
/*!40000 ALTER TABLE `divisoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `extrato`
--

DROP TABLE IF EXISTS `extrato`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `extrato` (
  `id` int NOT NULL AUTO_INCREMENT,
  `remetente` bigint NOT NULL,
  `receptor` bigint NOT NULL,
  `comando` varchar(20) DEFAULT NULL,
  `quantidade` int NOT NULL,
  `carta` int DEFAULT NULL,
  `data` date DEFAULT (curdate()),
  `hora` time DEFAULT (curtime()),
  `cartas` text,
  PRIMARY KEY (`id`),
  KEY `idx_receptor` (`receptor`),
  KEY `idx_remetente` (`remetente`),
  KEY `fk_carta_extrato` (`carta`),
  CONSTRAINT `fk_carta_extrato` FOREIGN KEY (`carta`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user2_extrato` FOREIGN KEY (`receptor`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_extrato` FOREIGN KEY (`remetente`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `extrato`
--

LOCK TABLES `extrato` WRITE;
/*!40000 ALTER TABLE `extrato` DISABLE KEYS */;
/*!40000 ALTER TABLE `extrato` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gerencia`
--

DROP TABLE IF EXISTS `gerencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gerencia` (
  `cod` int NOT NULL AUTO_INCREMENT,
  `adm` varchar(100) DEFAULT NULL,
  `operaçao` varchar(100) DEFAULT NULL,
  `data` date DEFAULT (curdate()),
  `destinatario` bigint DEFAULT NULL,
  `quantidade` int DEFAULT NULL,
  `card` int DEFAULT NULL,
  PRIMARY KEY (`cod`),
  KEY `adm` (`adm`),
  KEY `fk_gerencia_card` (`card`),
  CONSTRAINT `fk_gerencia_card` FOREIGN KEY (`card`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `gerencia_ibfk_1` FOREIGN KEY (`adm`) REFERENCES `usuarios` (`username`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gerencia`
--

LOCK TABLES `gerencia` WRITE;
/*!40000 ALTER TABLE `gerencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `gerencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario`
--

DROP TABLE IF EXISTS `inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario` (
  `id_user` bigint NOT NULL,
  `id_carta` int NOT NULL,
  `quantidade` int NOT NULL,
  PRIMARY KEY (`id_user`,`id_carta`),
  KEY `idx_id_carta` (`id_carta`),
  KEY `idx_id_user` (`id_user`),
  KEY `idx_id_carta_qtd` (`id_carta`,`quantidade` DESC),
  CONSTRAINT `fk_id_carta` FOREIGN KEY (`id_carta`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_id_user` FOREIGN KEY (`id_user`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario`
--

LOCK TABLES `inventario` WRITE;
/*!40000 ALTER TABLE `inventario` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `laranjas`
--

DROP TABLE IF EXISTS `laranjas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `laranjas` (
  `matriz` bigint NOT NULL,
  `laranja` bigint NOT NULL,
  PRIMARY KEY (`matriz`,`laranja`),
  KEY `laranja` (`laranja`),
  CONSTRAINT `laranjas_ibfk_1` FOREIGN KEY (`matriz`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE,
  CONSTRAINT `laranjas_ibfk_2` FOREIGN KEY (`laranja`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `laranjas`
--

LOCK TABLES `laranjas` WRITE;
/*!40000 ALTER TABLE `laranjas` DISABLE KEYS */;
/*!40000 ALTER TABLE `laranjas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `midiasesp`
--

DROP TABLE IF EXISTS `midiasesp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `midiasesp` (
  `id_user` bigint NOT NULL,
  `id_carta` int NOT NULL,
  `midia` varchar(300) NOT NULL,
  `tipo` varchar(10) DEFAULT NULL,
  `deletehash` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id_user`,`id_carta`),
  KEY `fk_midiasesp_carta` (`id_carta`),
  CONSTRAINT `fk_midiasesp_carta` FOREIGN KEY (`id_carta`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_midiasesp_telegram` FOREIGN KEY (`id_user`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `midiasesp`
--

LOCK TABLES `midiasesp` WRITE;
/*!40000 ALTER TABLE `midiasesp` DISABLE KEYS */;
/*!40000 ALTER TABLE `midiasesp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `multisub`
--

DROP TABLE IF EXISTS `multisub`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `multisub` (
  `id` int NOT NULL,
  `subcategoria` varchar(100) NOT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`,`subcategoria`),
  KEY `fk_sub` (`categoria`,`subcategoria`),
  CONSTRAINT `fk_carta` FOREIGN KEY (`id`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_sub` FOREIGN KEY (`categoria`, `subcategoria`) REFERENCES `divisoes` (`categoria`, `subcategoria`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `multisub`
--

LOCK TABLES `multisub` WRITE;
/*!40000 ALTER TABLE `multisub` DISABLE KEYS */;
INSERT INTO `multisub` VALUES (1063,'NCT 127','ASIAFARM'),(1064,'NCT 127','ASIAFARM');
/*!40000 ALTER TABLE `multisub` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfis`
--

DROP TABLE IF EXISTS `perfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfis` (
  `id` bigint NOT NULL,
  `card1` int DEFAULT NULL,
  `card2` int DEFAULT NULL,
  `card3` int DEFAULT NULL,
  `card_fav` int DEFAULT NULL,
  `sub_fav` varchar(100) DEFAULT NULL,
  `bio` text,
  `presets` varchar(300) DEFAULT NULL,
  `deletehash` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_card1` (`card1`),
  KEY `fk_card2` (`card2`),
  KEY `fk_card3` (`card3`),
  KEY `fk_cardfav` (`card_fav`),
  KEY `fk_favsub` (`sub_fav`),
  CONSTRAINT `fk_card1` FOREIGN KEY (`card1`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_card2` FOREIGN KEY (`card2`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_card3` FOREIGN KEY (`card3`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cardfav` FOREIGN KEY (`card_fav`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_favsub` FOREIGN KEY (`sub_fav`) REFERENCES `divisoes` (`subcategoria`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user` FOREIGN KEY (`id`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfis`
--

LOCK TABLES `perfis` WRITE;
/*!40000 ALTER TABLE `perfis` DISABLE KEYS */;
/*!40000 ALTER TABLE `perfis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `saboreados`
--

DROP TABLE IF EXISTS `saboreados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `saboreados` (
  `id_user` bigint NOT NULL,
  `subcategoria` varchar(100) NOT NULL,
  `categoria` varchar(100) NOT NULL,
  PRIMARY KEY (`id_user`,`subcategoria`),
  KEY `categoria` (`categoria`,`subcategoria`),
  CONSTRAINT `saboreados_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `saboreados_ibfk_2` FOREIGN KEY (`categoria`, `subcategoria`) REFERENCES `divisoes` (`categoria`, `subcategoria`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `saboreados`
--

LOCK TABLES `saboreados` WRITE;
/*!40000 ALTER TABLE `saboreados` DISABLE KEYS */;
/*!40000 ALTER TABLE `saboreados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `nome` varchar(255) NOT NULL,
  `imagem` varchar(255) DEFAULT NULL,
  `deletehash` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES ('HLE','https://i.imgur.com/YTCQT7h.jpeg','4vF5Kclks68WKgI');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `telegram_id` bigint NOT NULL,
  `sementes` int DEFAULT '0',
  `giros` int DEFAULT '24',
  `vip` tinyint(1) DEFAULT '0',
  `perfil` varchar(300) DEFAULT NULL,
  `parceiro` varchar(100) DEFAULT NULL,
  `ultimo_daily` date DEFAULT NULL,
  `username` varchar(100) DEFAULT NULL,
  `top` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `telegram_id` (`telegram_id`),
  UNIQUE KEY `idx_unique_id_user` (`username`),
  KEY `fk_parceiro` (`parceiro`),
  CONSTRAINT `usuarios_chk_1` CHECK ((`top` in (0,1)))
) ENGINE=InnoDB AUTO_INCREMENT=1034 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlists`
--

DROP TABLE IF EXISTS `wishlists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlists` (
  `id_user` bigint NOT NULL,
  `id_carta` int NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_user`,`id_carta`),
  KEY `wishlists_ibfk_1` (`id_carta`),
  CONSTRAINT `wishlists_ibfk_1` FOREIGN KEY (`id_carta`) REFERENCES `cartas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `wishlists_ibfk_2` FOREIGN KEY (`id_user`) REFERENCES `usuarios` (`telegram_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlists`
--

LOCK TABLES `wishlists` WRITE;
/*!40000 ALTER TABLE `wishlists` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlists` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'berrybot'
--
/*!50106 SET @save_time_zone= @@TIME_ZONE */ ;
/*!50106 DROP EVENT IF EXISTS `att_extrato` */;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `att_extrato` ON SCHEDULE EVERY 1 DAY STARTS '2025-06-09 17:27:00' ON COMPLETION NOT PRESERVE ENABLE DO DELETE FROM extrato WHERE data < CURDATE() - INTERVAL 7 DAY */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `att_gerencia` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `att_gerencia` ON SCHEDULE EVERY 1 DAY STARTS '2025-06-09 17:16:29' ON COMPLETION NOT PRESERVE ENABLE DO DELETE FROM gerencia WHERE data < CURDATE() - INTERVAL 7 DAY */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `atualizar_giros` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `atualizar_giros` ON SCHEDULE EVERY 12 HOUR STARTS '2025-03-15 00:00:00' ON COMPLETION NOT PRESERVE ENABLE DO CALL giros_diarios() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;

--
-- Dumping routines for database 'berrybot'
--
/*!50003 DROP PROCEDURE IF EXISTS `giros_diarios` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `giros_diarios`()
BEGIN
    UPDATE usuarios
    SET giros = LEAST(giros + 12, 1000)
    WHERE vip = 0;

    UPDATE usuarios
    SET giros = LEAST(giros + 15, 2000)
    WHERE vip = 1;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-17 12:23:25
