-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Creato il: Ago 07, 2021 alle 17:06
-- Versione del server: 10.4.8-MariaDB
-- Versione PHP: 7.3.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `maadb_project`
--
CREATE DATABASE IF NOT EXISTS `maadb_project` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `maadb_project`;

-- --------------------------------------------------------

--
-- Struttura della tabella `emoji_contenuta`
--

DROP TABLE IF EXISTS `emoji_contenuta`;
CREATE TABLE `emoji_contenuta` (
  `emoji` varchar(1) NOT NULL,
  `id_tweet` int(32) NOT NULL,
  `quantita` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `emoticon_contenuta`
--

DROP TABLE IF EXISTS `emoticon_contenuta`;
CREATE TABLE `emoticon_contenuta` (
  `emoticon` varchar(6) NOT NULL,
  `id_tweet` int(32) NOT NULL,
  `quantita` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `hashtag_contenuto`
--

DROP TABLE IF EXISTS `hashtag_contenuto`;
CREATE TABLE `hashtag_contenuto` (
  `hashtag` varchar(20) NOT NULL,
  `id_tweet` int(32) NOT NULL,
  `quantita` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `messaggio_twitter`
--

DROP TABLE IF EXISTS `messaggio_twitter`;
CREATE TABLE `messaggio_twitter` (
  `id` int(32) NOT NULL,
  `messaggio` text NOT NULL,
  `emozione` enum('anger','anticipation','disgust','fear','joy','sadness','surprise','trust') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `parola`
--

DROP TABLE IF EXISTS `parola`;
CREATE TABLE `parola` (
  `parola` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `parola_contenuta`
--

DROP TABLE IF EXISTS `parola_contenuta`;
CREATE TABLE `parola_contenuta` (
  `parola` varchar(32) NOT NULL,
  `id_tweet` int(32) NOT NULL,
  `quantita` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Struttura della tabella `risorsa_lessicale`
--

DROP TABLE IF EXISTS `risorsa_lessicale`;
CREATE TABLE `risorsa_lessicale` (
  `risorsa` enum('EmoSN','NRC','sentisense') NOT NULL,
  `emozione` enum('anger','anticipation','disgust','fear','joy','sadness','surprise','trust') NOT NULL,
  `id` int(32) NOT NULL,
  `parola` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `emoji_contenuta`
--
ALTER TABLE `emoji_contenuta`
  ADD PRIMARY KEY (`emoji`,`id_tweet`),
  ADD KEY `id_tweet_fk1` (`id_tweet`);

--
-- Indici per le tabelle `emoticon_contenuta`
--
ALTER TABLE `emoticon_contenuta`
  ADD PRIMARY KEY (`emoticon`,`id_tweet`),
  ADD KEY `id_tweet_fk` (`id_tweet`);

--
-- Indici per le tabelle `hashtag_contenuto`
--
ALTER TABLE `hashtag_contenuto`
  ADD PRIMARY KEY (`hashtag`,`id_tweet`),
  ADD KEY `id_tweet_fk2` (`id_tweet`);

--
-- Indici per le tabelle `messaggio_twitter`
--
ALTER TABLE `messaggio_twitter`
  ADD PRIMARY KEY (`id`);

--
-- Indici per le tabelle `parola`
--
ALTER TABLE `parola`
  ADD PRIMARY KEY (`parola`);

--
-- Indici per le tabelle `parola_contenuta`
--
ALTER TABLE `parola_contenuta`
  ADD PRIMARY KEY (`parola`,`id_tweet`),
  ADD KEY `id_tweet_fk3` (`id_tweet`);

--
-- Indici per le tabelle `risorsa_lessicale`
--
ALTER TABLE `risorsa_lessicale`
  ADD PRIMARY KEY (`id`),
  ADD KEY `parola` (`parola`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `messaggio_twitter`
--
ALTER TABLE `messaggio_twitter`
  MODIFY `id` int(32) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT per la tabella `risorsa_lessicale`
--
ALTER TABLE `risorsa_lessicale`
  MODIFY `id` int(32) NOT NULL AUTO_INCREMENT;

--
-- Limiti per le tabelle scaricate
--
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
