<?php 
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<div class="error notice is-dismissible">
	<p><?php WaicHtml::echoEscapedHtml($this->props['message']); ?></p>
</div>