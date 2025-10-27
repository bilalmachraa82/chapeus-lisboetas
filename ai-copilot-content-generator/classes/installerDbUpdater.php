<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
class WaicInstallerDbUpdater {
	public static function runUpdate( $current_version ) {
		if ($current_version && version_compare($current_version, '1.1.1', '<')) {
			WaicDb::query( "ALTER TABLE `@__tasks` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci");
			WaicDb::query( "ALTER TABLE `@__posts_create` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci");
		}
		
		if ( WaicDb::get( "SELECT 1 FROM `@__modules` WHERE code='postsfields'", 'one' ) != 1 ) {
			WaicDb::query( "INSERT INTO `@__modules` (id, code, active, type_id, label) VALUES (NULL, 'postsfields', 1, 1, 'PostsFields');" );
		}
		if ( WaicDb::get( "SELECT 1 FROM `@__modules` WHERE code='chatbots'", 'one' ) != 1 ) {
			WaicDb::query( "INSERT INTO `@__modules` (id, code, active, type_id, label) VALUES (NULL, 'chatbots', 1, 1, 'Chatbots');" );
		}
		if ( WaicDb::get( "SELECT 1 FROM `@__modules` WHERE code='promo'", 'one' ) != 1 ) {
			WaicDb::query( "INSERT INTO `@__modules` (id, code, active, type_id, label) VALUES (NULL, 'promo', 1, 1, 'Promo');" );
		}
		if ( WaicDb::get( "SELECT 1 FROM `@__modules` WHERE code='magictext'", 'one' ) != 1 ) {
			WaicDb::query( "INSERT INTO `@__modules` (id, code, active, type_id, label) VALUES (NULL, 'magictext', 1, 1, 'Magictext');" );
		}
		if ( WaicDb::get( "SELECT 1 FROM `@__modules` WHERE code='mcp'", 'one' ) != 1 ) {
			WaicDb::query( "INSERT INTO `@__modules` (id, code, active, type_id, label) VALUES (NULL, 'mcp', 1, 1, 'MCP');" );
		}
		if ( WaicDb::get( "SELECT 1 FROM `@__modules` WHERE code='forms'", 'one' ) != 1 ) {
			WaicDb::query( "INSERT INTO `@__modules` (id, code, active, type_id, label) VALUES (NULL, 'forms', 1, 1, 'Forms');" );
		}
		if ( ! WaicDb::existsTableColumn( '@__tasks', 'cycle' ) ) {
			WaicDb::query( 'ALTER TABLE `@__tasks` ADD COLUMN `cycle` INT NOT NULL DEFAULT 0 AFTER `steps`' );
			WaicDb::query( "ALTER TABLE `@__tasks` ADD COLUMN `message` VARCHAR(250) DEFAULT '' AFTER `cycle`" );
		}
		if ( ! WaicDb::existsTableColumn( '@__tasks', 'title' ) ) {
			WaicDb::query( "ALTER TABLE `@__tasks` ADD COLUMN `title` VARCHAR(250) DEFAULT '' AFTER `author`" );
		}
		if ( ! WaicDb::existsTableColumn( '@__tasks', 'tokens' ) ) {
			WaicDb::query( "ALTER TABLE `@__tasks` ADD COLUMN `tokens` BIGINT NOT NULL DEFAULT 0 AFTER `message`" );
		}
		if ( ! WaicDb::existsTableColumn( '@__tasks', 'mode' ) ) {
			WaicDb::query( "ALTER TABLE `@__tasks` ADD COLUMN `mode` VARCHAR(24) DEFAULT '' AFTER `tokens`" );
			WaicDb::query( "ALTER TABLE `@__tasks` ADD COLUMN `obj_id` BIGINT NOT NULL DEFAULT 0 AFTER `mode`" );
		}
		
		if ( ! WaicDb::existsTableColumn( '@__posts_create', 'added' ) ) {
			WaicDb::query( 'ALTER TABLE `@__posts_create` ADD COLUMN `added` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `post_id`' );
			WaicDb::query( "ALTER TABLE `@__posts_create` ADD COLUMN `uniq` VARCHAR(32) NULL AFTER `added`" );
		}
		if ( ! WaicDb::existsTableColumn( '@__history', 'feature' ) ) {
			WaicDb::query( "ALTER TABLE `@__history` ADD COLUMN `feature` VARCHAR(24) NOT NULL AFTER `task_id`" );
		}
		if ( ! WaicDb::existsTableColumn( '@__history', 'engine' ) ) {
			WaicDb::query( "ALTER TABLE `@__history` ADD COLUMN `engine` VARCHAR(20) DEFAULT '' AFTER `ip`" );
		}
		if ( WaicDb::get( "SELECT 1 FROM `@__tasks` WHERE feature='magictext'", 'one' ) != 1 ) {
			WaicDb::query( "INSERT INTO `@__tasks` (id, feature, title, author, status) VALUES (NULL, 'magictext', 'Magic Text', 0, 4);");
		}
	}
}
