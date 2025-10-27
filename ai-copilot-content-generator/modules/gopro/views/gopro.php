<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
class WaicGoproView extends WaicView {

	public function showGopro() {
		$frame = WaicFrame::_();
		//WaicAssets::_()->loadAdminEndCss();
		WaicDispatcher::doAction('getLicenseAssets');
		
		$this->assign('is_pro', $frame->isPro(false));
		$this->assign('license_data', WaicDispatcher::applyFilters('getLicenseData', array()));
		$this->assign('extendUrl', 'https://aiwuplugin.com/');

		return parent::getContent('adminLicense');
		return '';
	}
}
