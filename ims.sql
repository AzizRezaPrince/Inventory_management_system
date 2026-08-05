-- phpMyAdmin SQL Dump
-- version 3.2.4
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 17, 2015 at 09:18 PM
-- Server version: 5.1.41
-- PHP Version: 5.3.1

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `ims`
--

-- --------------------------------------------------------

--
-- Table structure for table `currentstocks`
--

CREATE TABLE IF NOT EXISTS `currentstocks` (
  `productcode` varchar(100) NOT NULL,
  `quantity` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `currentstocks`
--

INSERT INTO `currentstocks` (`productcode`, `quantity`) VALUES
('p2', 30),
('p1', 1),
('p10', 0),
('prod1', 1),
('prod5', 35),
('prod3', 0),
('prod2', 0);

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE IF NOT EXISTS `customers` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `customercode` varchar(100) NOT NULL,
  `fullname` varchar(50) NOT NULL,
  `location` varchar(50) NOT NULL,
  `phone` varchar(50) NOT NULL,
  PRIMARY KEY (`cid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`cid`, `customercode`, `fullname`, `location`, `phone`) VALUES
(2, 'cus3', 'ram', 'ktm', '331');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE IF NOT EXISTS `products` (
  `pid` int(11) NOT NULL AUTO_INCREMENT,
  `productcode` varchar(100) NOT NULL,
  `productname` varchar(50) NOT NULL,
  `costprice` double NOT NULL,
  `sellingprice` double NOT NULL,
  `brand` varchar(50) NOT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=79 ;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`pid`, `productcode`, `productname`, `costprice`, `sellingprice`, `brand`) VALUES
(73, 'prod3', 'qq', 3, 2, '4d'),
(72, 'prod2', 'pen', 20, 30, 'techno'),
(71, 'prod1', 'wai wai', 400, 450, 'cg'),
(74, 'prod4', 'wai wai', 400, 450, 'cg2'),
(78, 'prod5', 'Mobile', 500, 700, 'cg');

-- --------------------------------------------------------

--
-- Table structure for table `purchaseinfo`
--

CREATE TABLE IF NOT EXISTS `purchaseinfo` (
  `purchaseid` int(11) NOT NULL AUTO_INCREMENT,
  `suppliercode` varchar(200) NOT NULL,
  `productcode` varchar(200) NOT NULL,
  `date` varchar(200) NOT NULL,
  `quantity` int(11) NOT NULL,
  `totalcost` double NOT NULL,
  PRIMARY KEY (`purchaseid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=30 ;

--
-- Dumping data for table `purchaseinfo`
--

INSERT INTO `purchaseinfo` (`purchaseid`, `suppliercode`, `productcode`, `date`, `quantity`, `totalcost`) VALUES
(19, 's1', 'p2', 'Wed Jan 14 00:15:19 NPT 2015', 40, 1320),
(20, 's1', 'p1', 'Wed Jan 07 16:42:44 NPT 2015', 4, 80000),
(21, 's6', 'p10', 'Tue Jan 06 16:51:44 NPT 2015', 20, 400000),
(22, 'sup4', 'prod1', 'Thu Jan 15 15:25:45 NPT 2015', 4, 1600),
(23, 'sup5', 'prod1', 'Thu Jan 15 00:00:00 NPT 2015', 6, 2400),
(24, 'sup4', 'prod5', 'Fri Jan 16 22:14:10 NPT 2015', 30, 15000),
(25, 'sup18', 'prod5', 'Sat Jan 17 22:23:52 NPT 2015', 5, 2500),
(26, 'sup18', 'prod3', 'Fri Jan 16 00:00:00 NPT 2015', 4, 12),
(27, 'sup18', 'prod2', 'Fri Jan 16 22:42:33 NPT 2015', 10, 200),
(28, 'sup71', 'prod1', 'Thu Jan 22 23:06:32 NPT 2015', 1, 600),
(29, 'sup4', 'prod2', 'Fri Jan 16 23:09:17 NPT 2015', 5, 150);

-- --------------------------------------------------------

--
-- Table structure for table `salesreport`
--

CREATE TABLE IF NOT EXISTS `salesreport` (
  `salesid` int(11) NOT NULL AUTO_INCREMENT,
  `date` varchar(40) NOT NULL,
  `productcode` varchar(100) NOT NULL,
  `customercode` varchar(100) NOT NULL,
  `quantity` int(11) NOT NULL,
  `revenue` double NOT NULL,
  `soldby` varchar(50) NOT NULL,
  PRIMARY KEY (`salesid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=6 ;

--
-- Dumping data for table `salesreport`
--

INSERT INTO `salesreport` (`salesid`, `date`, `productcode`, `customercode`, `quantity`, `revenue`, `soldby`) VALUES
(1, 'Fri Jan 16 23:12:40 NPT 2015', 'prod2', 'cus3', 4, 120, 'user4'),
(2, 'Thu Jan 08 21:30:51 NPT 2015', 'prod1', 'cus3', 5, 2250, 'sazanrjb'),
(3, 'Thu Jan 15 21:26:47 NPT 2015', 'prod1', 'cus3', 5, 2250, 'sazanrjb'),
(4, 'Sat Jan 17 10:08:20 NPT 2015', 'prod3', 'cus3', 1, 2, 'user4');

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE IF NOT EXISTS `suppliers` (
  `sid` int(11) NOT NULL AUTO_INCREMENT,
  `suppliercode` varchar(100) NOT NULL,
  `fullname` varchar(50) NOT NULL,
  `location` varchar(50) NOT NULL,
  `phone` varchar(10) NOT NULL,
  PRIMARY KEY (`sid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=143 ;

--
-- Dumping data for table `suppliers`
--

INSERT INTO `suppliers` (`sid`, `suppliercode`, `fullname`, `location`, `phone`) VALUES
(69, 'sup5', 'manish', 'ktm', '4123372'),
(68, 'sup4', 'sia', 'US', '11623231'),
(67, 'sup3', 'shyam', 'bkt', '4121233'),
(66, 'sup2', 'hari', 'pkr', '4121216'),
(65, 'sup1', 'ram', 'ktm', '4284232'),
(72, 'sup8', 'suman', 'sanepa', '9849266371'),
(73, 'sup8', 'john', 'sankhu', '9849266322'),
(74, 'sup9', 'gsg', 'hd', '1'),
(75, 'sup11', 'dd', 'dd', '22'),
(76, 'sup12', 'sdw', 'dws', '222'),
(77, 'sup8', 'paras', 'nepal', '123'),
(78, 'sup8', 'parase', 'nepal', '123'),
(79, 'sup14', 'ds', 'sd', '2'),
(82, 'sup15', 'suman', 'sanepa', '9849266371'),
(83, 'sup16', 'ram', 'ktm', '4284232'),
(84, 'sup17', 'hari', 'pkr', '4121216'),
(85, 'sup18', 'hari', 'pkr', '4121216'),
(86, 'sup19', 'john', 'sankhu', '9849266322'),
(87, 'sup20', 'john', 'sankhu', '9849266322'),
(88, 'sup21', 'john', 'sankhu', '9849266322'),
(89, 'sup22', 'john', 'sankhu', '9849266322'),
(90, 'sup23', 'john', 'sankhu', '9849266322'),
(91, 'sup24', 'john', 'sankhu', '9849266322'),
(92, 'sup25', 'john', 'sankhu', '9849266322'),
(93, 'sup26', 'john', 'sankhu', '9849266322'),
(94, 'sup27', 'john', 'sankhu', '9849266322'),
(95, 'sup28', 'john', 'sankhu', '9849266322'),
(96, 'sup29', 'john', 'sankhu', '9849266322'),
(97, 'sup30', 'john', 'sankhu', '9849266322'),
(98, 'sup31', 'john', 'sankhu', '9849266322'),
(99, 'sup32', 'john', 'sankhu', '9849266322'),
(100, 'sup33', 'john', 'sankhu', '9849266322'),
(101, 'sup34', 'john', 'sankhu', '9849266322'),
(102, 'sup35', 'john', 'sankhu', '9849266322'),
(103, 'sup36', 'john', 'sankhu', '9849266322'),
(104, 'sup37', 'john', 'sankhu', '9849266322'),
(105, 'sup38', 'john', 'sankhu', '9849266322'),
(106, 'sup39', 'john', 'sankhu', '9849266322'),
(107, 'sup40', 'john', 'sankhu', '9849266322'),
(108, 'sup41', 'john', 'sankhu', '9849266322'),
(109, 'sup42', 'john', 'sankhu', '9849266322'),
(110, 'sup43', 'john', 'sankhu', '9849266322'),
(111, 'sup44', 'john', 'sankhu', '9849266322'),
(112, 'sup45', 'john', 'sankhu', '9849266322'),
(113, 'sup46', 'john', 'sankhu', '9849266322'),
(114, 'sup47', 'john', 'sankhu', '9849266322'),
(115, 'sup48', 'john', 'sankhu', '9849266322'),
(116, 'sup49', 'john', 'sankhu', '9849266322'),
(117, 'sup50', 'john', 'sankhu', '9849266322'),
(118, 'sup51', 'john', 'sankhu', '9849266322'),
(119, 'sup52', 'john', 'sankhu', '9849266322'),
(120, 'sup53', 'john', 'sankhu', '9849266322'),
(121, 'sup54', 'john', 'sankhu', '9849266322'),
(122, 'sup55', 'john', 'sankhu', '9849266322'),
(123, 'sup56', 'john', 'sankhu', '9849266322'),
(124, 'sup57', 'john', 'sankhu', '9849266322'),
(125, 'sup58', 'john', 'sankhu', '9849266322'),
(126, 'sup59', 'john', 'sankhu', '9849266322'),
(127, 'sup60', 'john', 'sankhu', '9849266322'),
(128, 'sup61', 'john', 'sankhu', '9849266322'),
(129, 'sup62', 'john', 'sankhu', '9849266322'),
(130, 'sup63', 'john', 'sankhu', '9849266322'),
(131, 'sup64', 'john', 'sankhu', '9849266322'),
(132, 'sup65', 'john', 'sankhu', '9849266322'),
(133, 'sup66', 'john', 'sankhu', '9849266322'),
(134, 'sup67', 'john', 'sankhu', '9849266322'),
(135, 'sup68', 'sdw', 'dws', '222'),
(136, 'sup69', 'sdw', 'dws', '222'),
(137, 'sup70', 'ram', 'ktm', '4284232'),
(138, 'sup71', 'ram', 'ktm', '4284232'),
(139, 'sup72', 'rame', 'ektm', '42842323'),
(140, 'sup73', 'ddd', 'dd', '22'),
(141, 'sup74', 'teyww', 'ktmrrrrrrrrr3', '4282842'),
(142, 'sup75', 'manish', 'aktm', '4123372');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fullname` varchar(50) NOT NULL,
  `location` varchar(50) NOT NULL,
  `phone` varchar(10) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(200) NOT NULL,
  `category` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=56 ;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `fullname`, `location`, `phone`, `username`, `password`, `category`) VALUES
(54, 'Sajan Rajbhandari', 'Pokhara', '9849284991', 'user4', 'c4ca4238a0b923820dcc509a6f75849b', 'ADMINISTRATOR');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
