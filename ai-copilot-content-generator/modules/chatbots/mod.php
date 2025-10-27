<?php
class WaicChatbots extends WaicModule {
	public function init() {
		add_shortcode(WAIC_CHATBOT, array($this, 'renderChatbot'));
		WaicDispatcher::addFilter('mainAdminTabs', array($this, 'addAdminTab'));
		WaicDispatcher::addFilter('addTaskColumns_chatbots', array($this, 'addTaskColumns'), 10, 3);
	}
	
	public function addAdminTab( $tabs ) {
		$code = 'workspace';
		$tabs['chatbots']   = array(
			'label'      => esc_html__( 'Create AI Chatbot', 'ai-copilot-content-generator' ),
			'callback'   => array( $this, 'showChatbotsTabContent' ),
			'hidden'     => 1,
			'sort_order' => 0,
			'bread'      => true,
			'last_Id' => 'waicTaskNameWrapper',
		);
		return $tabs;
	}
	
	public function showChatbotsTabContent() {
		$taskId = WaicReq::getVar('task_id');
		$title = __( 'Your Scenario name', 'ai-copilot-content-generator' );
		if (!empty($taskId)) {
			$taskTitle = WaicFrame::_()->getModule('workspace')->getModel('tasks')->getTaskTitle($taskId);
			if (!is_null($taskTitle) && !empty($taskTitle)) {
				$title = $taskTitle;
			}
		}
		WaicFrame::_()->getModule('adminmenu')->setLastBread($title);
		return $this->getView()->showCreateTabContent($taskId);
	}
	public function getChatbotsTabsList( $current = '' ) {
		$tabs = array(
			'general' => array(
				'class' => '',
				'pro' => false,
				'label' => __('General', 'ai-copilot-content-generator'),
			),
			'api' => array(
				'class' => '',
				'pro' => false,
				'label' => __('API settings', 'ai-copilot-content-generator'),
			),
			'context' => array(
				'class' => '',
				'pro' => false,
				'label' => __('Context', 'ai-copilot-content-generator'),
			),
			'appearance' => array(
				'class' => '',
				'pro' => false,
				'label' => __('Appearance', 'ai-copilot-content-generator'),
			),
			'history' => array(
				'class' => '',
				'pro' => false,
				'label' => __('History', 'ai-copilot-content-generator'),
			),
		);

		if (empty($current) || !isset($tabs[$current])) {
			reset($tabs);
			$current = key($tabs);
		}
		$tabs[$current]['class'] .= ' current';
		
		return $tabs;
	}
	public function getChatbotsPresetsList() {
		$list = array(
			'default' => array(
				'label' => 'AIWU',
				'pro' => false,
			),
		);
		return $list;
	}
	public function getAiChatbotImages( $type, $exts = array('png', 'svg') ) {
		$path = WAIC_MODULES_DIR . 'chatbots/assets/img/' . $type;
		$found = array();
		if (file_exists(stream_resolve_include_path($path))) {
			$dir = opendir($path);
			$path .= '/';
			while ( ( $file = readdir($dir) ) !== false ) {
				if ( '.' == $file || '..' == $file ) {
					continue;
				}
				if (is_file($path . $file)) {
					$len = strlen($file) - 1;
					foreach ($exts as $e) {
						if (strripos($file, '.' . $e) + strlen($e) == $len ) {
							$found[] = $file;
							break;
						}
					}
				}
			}
			closedir($dir);
		}
		return $found;
	}
	public function renderChatbot( $params ) {
		$p = array(
			'id' => ( isset($params['id']) ? (int) $params['id'] : 0 ),
			'mode' => ( isset($params['mode']) && 'widget' == $params['mode'] ? 'widget' : '' ),
		);
		return $this->getView()->renderChatbotHtml($p, $params['id']);
	}
	public function addTaskColumns( $columns, $params, $taskId ) {
		if (empty($taskId)) {
			$columns['status'] = 4;
		} else {
			unset($columns['status']);
		}
		return $columns;
	}
}
