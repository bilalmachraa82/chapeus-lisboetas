<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class WaicAiproviderModel extends WaicModel implements WaicAIProviderInterface {

	private $provider = null;
	private $imageProvider = null;
	private $taskId;
	private $feature = '';
	private $userId;
	private $userIP;
	private $genMode;
	private $saveError = true;
	
	public function getEngine( $type = '' ) {
		switch ( $type ) {
			case 'image':
				return $this->imageProvider->getEngine();
			default:
				return $this->provider->getEngine();
		}
	}

	public function getInstance( $params ) {
		$defaults = WaicFrame::_()->getModule('options')->getModel()->getDefaults('api');

		$this->provider = $this->getModule()->getModel($this->getModelName(WaicUtils::getArrayValue($params, 'engine')));
		$this->imageProvider = $this->getModule()->getModel($this->getModelName(WaicUtils::getArrayValue($params, 'image_engine', $defaults['image_engine'])));

		if ( !$this->provider ) {
			WaicFrame::_()->pushError(esc_html__('AI Provider not found', 'ai-copilot-content-generator'));
			return false;
		}

		return $this;
	}

	public function init( $taskId = 0, $userId = 0, $userIP = '', $genMode = 0, $saveError = true ) {
		$this->taskId = $taskId;
		$this->userId = $userId;
		$this->userIP = $userIP;
		$this->genMode = $genMode;
		$this->saveError = $saveError;
		if (!empty($taskId)) {
			$this->feature = WaicFrame::_()->getModule('workspace')->getModel('tasks')->getTaskFeature($taskId);
		}

		if ( $this->imageProvider ) {
			$this->imageProvider->init();
		}

		return $this->provider->init();
	}
	public function setFeature( $feature ) {
		$this->feature = $feature;
	}
	public function setSaveError( $saveError ) {
		$this->saveError = $saveError;
	}

	public function setApiOptions( $options ) {
		$result =  $this->provider->setApiOptions($options);
		if (false === $result && $this->saveError) {
			WaicFrame::_()->getModule('workspace')->getModel('tasks')->updateTask($this->taskId, array('status' => 7, 'message' => substr(WaicFrame::_()->getLastError(), 0, 240)));
		}

		if ( $this->imageProvider ) {
			$this->imageProvider->setApiOptions($options);
		}

		return $result;
	}

	public function getText( $params, $stream = null, $type = '' ) {
		$data = $this->provider->getText( $params, $stream );

		if (false === $data) {
			$results['error'] = 1;
			$results['msg'] = WaicFrame::_()->getLastError();

			return $results;
		}

		$results = $data['results'];
		$params = $data['params'];

		$history = $this->getHistory($results, $params, $type);

		$results['his_id'] = WaicFrame::_()->getModule('workspace')->getModel('history')->saveHistory($history);

		return $results;
	}

	public function getImage( $params ) {
		if ( !$this->imageProvider ) {
			WaicFrame::_()->pushError(esc_html__('Image AI Provider not found', 'ai-copilot-content-generator'));
			return false;
		}

		$data = $this->imageProvider->getImage( $params );

		if (false === $data) {
			$results['error'] = 1;
			$results['msg'] = WaicFrame::_()->getLastError();

			return $results;
		}


		$results = $data['results'];
		$params = $data['params'];

		$history = $this->getHistory($results, $params, '', 'image');

		$results['his_id'] = WaicFrame::_()->getModule('workspace')->getModel('history')->saveHistory($history);

		return $results;
	}

	private function getModelName( $engine ) {
		switch ($engine) {
			case 'deep-seek':
				return 'deepseek';
			case 'gemini':
				return 'gemini';
			case 'open-ai':
			default:
				return 'openai';
		}
	}

	private function getHistory( $results, $params, $type = '', $typeProvider = '' ) {
		$history = array(
			'engine' => $this->getEngine($typeProvider),
			'model' => empty($params['model']) ? $type : $params['model'],
			'task_id' => $this->taskId,
			'feature' => $this->feature,
			'user_id' => $this->userId,
			'ip' => $this->userIP,
			'mode' => $this->genMode,
		);
		$history['status'] = $results['error'];
		$history['tokens'] = $results['tokens'];

		return $history;
	}
	
	public function sendFile( $params ) {
		$data = $this->provider->sendFile( $params );

		if (false === $data) {
			$results['error'] = 1;
			$results['msg'] = WaicFrame::_()->getLastError();

			return $results;
		}

		$results = $data['results'];
		$params = $data['params'];

		$history = $this->getHistory($results, $params, 'train');

		$results['his_id'] = WaicFrame::_()->getModule('workspace')->getModel('history')->saveHistory($history);

		return $results;
	}
	public function getFineTunes( $params, $method = 'POST', $job = false ) {
		$data = $this->provider->getFineTunes( $params, $method, $job );

		if (false === $data) {
			$results['error'] = 1;
			$results['msg'] = WaicFrame::_()->getLastError();

			return $results;
		}

		$results = $data['results'];
		$params = $data['params'];

		$history = $this->getHistory($results, $params, 'check_train');

		$results['his_id'] = WaicFrame::_()->getModule('workspace')->getModel('history')->saveHistory($history);

		return $results;
	}
	public function sendEmbeddings( $params, $method = 'POST' ) {
		$data = $this->provider->sendEmbeddings( $params, $method );

		if (false === $data) {
			$results['error'] = 1;
			$results['msg'] = WaicFrame::_()->getLastError();

			return $results;
		}

		$results = $data['results'];
		$params = $data['params'];

		$history = $this->getHistory($results, $params, 'embeddings');

		$results['his_id'] = WaicFrame::_()->getModule('workspace')->getModel('history')->saveHistory($history);

		return $results;
	}
}
