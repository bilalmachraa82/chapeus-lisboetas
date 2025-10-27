<?php
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
class WaicChatbotsModel extends WaicModel {
	public function __construct() {
		$this->_setTbl('chatlogs');
	}
	public function isDeleteByCancel() {
		return false;
	}
	public function canUnpublish() {
		return true;
	}
	public function unpublishEtaps( $taskId ) {
		WaicFrame::_()->getModule('workspace')->getModel('tasks')->updateTask($taskId, array('status' => 6));
		return false;
	}
	public function publishResults( $taskId, $publish ) {
		WaicFrame::_()->getModule('workspace')->getModel('tasks')->updateTask($taskId, array('status' => 4));
		return false;
	}
	public function clearEtaps( $taskId, $ids = false, $withContent = true ) {
		if ($withContent) {
			WaicFrame::_()->getModule('workspace')->getModel('history')->deleteHistory($taskId);
			$query = 'DELETE t FROM @__chatlogs t WHERE NOT EXISTS(SELECT 1 FROM @__history h WHERE h.id=t.his_id)';
			WaicDb::query($query);
		}
		return true;
	}
	/*public function isAllPublished( $taskId ) {
		return true;
	}*/
	public function isActiveChat( $taskId = 0, $userId = 0, $ip = '', $mode = 0, $lifetime = 0 ) {
		$query = 'SELECT 1 FROM @__history' .
			' WHERE task_id=' . ( (int) $taskId ) .
			' AND mode=' . ( (int) $mode ) . 
			' AND user_id=' . ( (int) $userId ) .
			( empty($userId) ? " AND ip='" . $ip . "'" : '' );
		if (!empty($lifetime)) {
			$now = WaicUtils::getTimestampDB();
			$query .= " AND created>DATE_SUB('" . $now . "', INTERVAL " . $lifetime . ' MINUTE) ';
		}
		$query .= ' LIMIT 1';
		return ( WaicDb::get($query, 'one') == 1 );
	}
	public function getUserChatLog( $taskId = 0, $userId = 0, $ip = '', $mode = 0, $cnt = 0, $status = 0, $dd = false ) {
		$forDate = !empty($dd);
		$query = 'SELECT h.id as his_id, h.created, l.question, l.answer, h.status, l.file' .
			' FROM @__history as h' .
			' INNER JOIN @__chatlogs l ON (l.his_id=h.id)' .
			' WHERE h.task_id=' . ( (int) $taskId ) .
			( false !== $status ? ' AND h.status= ' . ( (int) $status ) : '' ) .
			' AND h.mode=' . ( (int) $mode ) .
			' AND h.user_id=' . ( (int) $userId ) .
			( empty($userId) || $forDate ? " AND ip='" . $ip . "'" : '' ) .
			( $forDate ? " AND h.created BETWEEN '" . $dd . " 00:00:00' AND '" . $dd . " 23:59:59'" : '' ) .
			' ORDER BY h.id' .
			( empty($cnt) ? '' : ' DESC LIMIT ' . ( (int) $cnt ) ); 
		$log = WaicDb::get($query);
		if ($log && !empty($log)) {
			if (!empty($cnt)) {
				$log = array_reverse($log);
			}
		} else {
			$log = array();
		}
		return $log;
	}
	public function deleteUserChatLog( $taskId = 0, $userId = 0, $ip = '', $mode = 0 ) {
		$query = 'DELETE l FROM @__chatlogs l' .
			' INNER JOIN @__history h ON (l.his_id=h.id)' .
			' WHERE h.status=0 AND h.task_id=' . ( (int) $taskId ) .
			' AND h.mode=' . ( (int) $mode ) .
			' AND ' . ( empty($userId) ? "ip='" . $ip . "'" : 'h.user_id=' . ( (int) $userId ) ); 
		WaicDb::query($query);
		return true;
	}
	public function humanRequest( $taskId ) {
		$workspace = WaicFrame::_()->getModule('workspace');
		$task = $workspace->getModel('tasks')->getTask($taskId);
		$params = WaicUtils::getArrayValue($task, 'params', array(), 2);
		$context = WaicUtils::getArrayValue($params, 'context', array(), 2);

		$newLog = array(
			'answer' => WaicUtils::getArrayValue($context, 'human_request_message', __('Please provide your email address so we can assist you further. Our team will get back to you within 24 hours. Thank you!', 'ai-copilot-content-generator')),
			'error' => 0,
			'need_email' => 1,
			'request' => 'human',
			'plh_email' => WaicUtils::getArrayValue($context, 'plh_email'),
		);

		return $newLog;
	}
	public function sendEmail( $email, $taskId, $mode, $request = '' ) {
		$workspace = WaicFrame::_()->getModule('workspace');
		$task = $workspace->getModel('tasks')->getTask($taskId);
		if (!$task || empty($task)) {
			return array('question' => __('Unexpected error.', 'ai-copilot-content-generator'), 'error' => 1);
		}
		$params = WaicUtils::getArrayValue($task, 'params', array(), 2);
		$context = WaicUtils::getArrayValue($params, 'context', array(), 2);
		
		$isError = ( 'error' == $request );
		$newLog = array(
			'answer' => __('Email is not correct', 'ai-copilot-content-generator'),
			'error' => $isError ? 1 : 0,
			'need_email' => 1,
		);
		if (!is_email($email)) {
			$newLog['answer'] =  WaicUtils::getArrayValue($context, 'error_email', $newLog['answer']);
			return $newLog;
		}
		$user = wp_get_current_user();
		$userId = $user ? $user->ID : 0;
		$isGuest = empty($userId);
		$ip = WaicUtils::getRealUserIp();
		
		$history = array(
			'task_id' => $taskId,
			'user_id' => $userId,
			'ip' => $ip, 
			'mode' => $mode,
			'status' => 3,
			'tokens' => 0,
		);
		$newLog = array(
			'his_id' => $workspace->getModel('history')->saveHistory($history),
			'question' => $email,
		);
		$this->insert($newLog);

		if (WaicUtils::getArrayValue($context, 'e_' . $request . '_request', 0, 1) != 1) {
			return $newLog;
		}
		$adminEmail = WaicUtils::getArrayValue($context, $request . '_admin_email');
		if (empty($adminEmail)) {
			return $newLog;
		}
		$headers = array(
			'Content-type: text/html; charset=utf-8',
			'Content-Transfer-Encoding: 8bit',
			'From: ' . get_option( 'woocommerce_email_from_name' ) . ' <' . get_option( 'woocommerce_email_from_address' ) . '>',
		);
		$subject = $isError ? 'Chatbot Error Request' : 'Chatbot Human Request';
		
		$message = 'A user has requested human assistance through the chatbot. Below are the details:' . PHP_EOL .
			'User Login: ' . ( $isGuest ? 'guest' : $user->user_login ) . PHP_EOL .
			'User Name: ' . ( $isGuest ? '' : $user->user_firstname . ' ' . $user->user_lastname ) . PHP_EOL .
			'User Email: ' . $email . PHP_EOL .
			'User IP: ' . $ip . PHP_EOL .
			'Date & Time: ' . WaicUtils::getTimestampDB() . PHP_EOL .
			'Chatbot Name: ' . $task['title'] . PHP_EOL . PHP_EOL .
			'Conversation Log: ' . PHP_EOL ;

		$log = $this->getUserChatLog($taskId, $userId, $ip, 0, 0, false);
		foreach ($log as $log) {
			if (!empty($log['file'])) {
				$message .= 'User (' . $log['created'] . '): File uploaded' . PHP_EOL;
			}
			if (!empty($log['question'])) {
				$message .= 'User (' . $log['created'] . '): ' . ( 3 == $log['status'] ? 'EMAIL - ' : '' ) . $log['question'] . PHP_EOL;
			}
			if (!empty($log['answer'])) {
				$message .= 'Bot (' . $log['created'] . '): ' . ( empty($log['status']) ? '' : 'ERROR - ' ) . $log['answer'] . PHP_EOL;
			}
		}

		$message .= PHP_EOL . 'Please follow up with the user as soon as possible.' . PHP_EOL . PHP_EOL .
			'Best regards,' . PHP_EOL .
			'AIWU plugin';
			
		if (!wp_mail($adminEmail, $subject, $message, $headers)) {
			WaicFrame::_()->pushError(__('Error by sending email', 'ai-copilot-content-generator'));
		}
		$newLog['answer'] = WaicUtils::getArrayValue($context, 'error_thank', __('Thank you', 'ai-copilot-content-generator'));
		$newLog['need_email'] = 0;
		$newLog['disable'] = $isError ? 1 : 0;

		return $newLog;
	}
	/*public function sendFile( $message, $files, $taskId, $mode ) {
		error_log('$files='.json_encode($files));
		if (empty($files['img'])) {
			return array('question' => __('Empty File', 'ai-copilot-content-generator'), 'error' => 1);
		}
		$file = $files['img'];
		
		$error = $this->controlUploatedFile($file);
		if (!empty($error)) {
			return array('question' => $error, 'error' => 1);
		}
		$workspace = WaicFrame::_()->getModule('workspace');
		$hisModel = $workspace->getModel('history');
		$task = $workspace->getModel('tasks')->getTask($taskId);
		if (!$task) {
			return array('answer' => __('Unexpected error', 'ai-copilot-content-generator'), 'error' => 1);
		}
		
		$user = wp_get_current_user();
		$userId = $user ? $user->ID : 0;
		$isGuest = empty($userId);
		$ip = WaicUtils::getRealUserIp();
		
		$params = WaicUtils::getArrayValue($task, 'params', array(), 2);
		
		$openAI = $workspace->getModel('openai')->init($taskId, $userId, $ip, $mode);
		if (!$openAI) {
			return false;
		}
		//f"data:image/png;base64,{base64_image}";
		$extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
		$f = base64_encode(file_get_contents($file['tmp_name']));
		$fStr = 'data:image/' . $extension . ";base64,{$f}";
		//if (empty($message)) 
		//$message = 'Что это?';
		$log = $this->sendMessage($message, $taskId, $mode, '', $fStr);
		return $log;
		
		
		$boundary = wp_generate_uuid4();
		$options = WaicUtils::getArrayValue($params, 'api', array(), 2);
		$options['contentType'] = 'multipart/form-data; boundary=' . $boundary;
		error_log('ffffffffffff');
		$openAI->setApiOptions($options);
		$opts = array(
			'boundary' => $boundary,
			'file_name' => sanitize_file_name($file['name']),
			'file_data' => file_get_contents($file['tmp_name']),
		);
		error_log(sanitize_file_name($file['name']));
		$result = $openAI->sendFile($opts);
		$newLog = array(
			'his_id' => $result['his_id'], 
			'question' => empty($result['file_id']) ? __('File not Uploaded', 'ai-copilot-content-generator') : __('File Uploaded', 'ai-copilot-content-generator'),
			'answer' => $result['error'] ? $this->controlText($result['msg']) : '',
			'typ' => 1,
		);
		if (!empty($result['his_id'])) {
			$this->insert($newLog);
		}

		if (empty($result['file_id'])) {
			//$context = WaicUtils::getArrayValue($params, 'context', array(), 2);
			$newLog['tt'] = WaicUtils::getFormatedDateTime(WaicUtils::getTimestamp(), 'H:i');
			//$msg = WaicUtils::getArrayValue($context, 'error_message');
			$newLog['answer'] = '';
			//if (!empty($msg)) {
			// $newLog['answer'] = $msg;
			//} 

			return $newLog;
		}
		$message = 'Analyze the attached file with ID: ' . $result['file_id'];
		$log = $this->sendMessage( $message, $taskId, $mode, '', 2);
		
		if (!empty($log['error'])) {
			$log['question'] = $newLog['question'];
		}
		
		return $log;
	}*/
	public function getFileString( $files, $maxSize ) { 
		$result = array(
			'file' => '',
			'error' => '',
		);
		
		if (empty($files['img'])) {
			$result['error'] = __('Empty File', 'ai-copilot-content-generator');
			return $result;
		}
		$file = $files['img'];
		
		$extensions = array('png', 'gif', 'jpeg', 'jpg');
		$error = WaicUtils::controlUploatedFile($file, $extensions);
		
		if (!empty($error)) {
			$result['error'] = $error;
			return $result;
		}
		$size = (int) $file['name'];
		if ($size > $maxSize) {
			$result['error'] = __('File is too big!', 'ai-copilot-content-generator');
			return $result;
		}
			
		$extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
		$f = base64_encode(file_get_contents($file['tmp_name']));
		$result['file'] = 'data:image/' . $extension . ";base64,{$f}";
		return $result;
	}
		
	public function sendMessage( $message, $taskId, $mode, $cAware = '', $files = false, $options = array() ) {
		$workspace = WaicFrame::_()->getModule('workspace');
		$task = $workspace->getModel('tasks')->getTask($taskId);
		if (!$task || empty($task)) {
			return array('question' => __('Unexpected error.', 'ai-copilot-content-generator'), 'error' => 1);
		}
		$params = WaicUtils::getArrayValue($task, 'params', array(), 2);
		
		$file = '';
		if ($files) {
			$api = WaicUtils::getArrayValue($params, 'api', array(), 2);
			$files = $this->getFileString($files, WaicUtils::getArrayValue($api, 'max_file_size', 5, 1) * 1048576);
			if (!empty($files['error'])) {
				return array('question' => $files['error'], 'error' => 1);
			}
			$file = $files['file'];
		}
		if (isset($options['user_id'])) {
			$user = empty($options['user_id']) ? false : get_user_by('id', (int) $options['user_id']);
		} else {
			$user = wp_get_current_user();
		}
		$userId = $user ? $user->ID : 0;
		$isGuest = empty($userId);
		$ip = isset($options['ip']) ? $options['ip'] : WaicUtils::getRealUserIp();
		
		$hisModel = $workspace->getModel('history');
	
		$general = WaicUtils::getArrayValue($params, 'general', array(), 2);
		$context = WaicUtils::getArrayValue($params, 'context', array(), 2);
		
		$isError = false;
		$allLimit = WaicUtils::getArrayValue($general, 'alltime_limit', 0, 1);
		if (!empty($allLimit)) {
			$where = array(
				'task_id' => $taskId,
				'mode' => 0,
			);
			$cntTokens = $hisModel->getCountTokens($where);
			if ($cntTokens >= $allLimit) {
				$isError = true;
				$errMsg = 'Exceeds value: All-Time Limit = ' . $allLimit;
				$task = $workspace->getModel('tasks')->updateTask($taskId, array('status' => 6));
			}
		}

		if (!$isError) {
			$monLimit = WaicUtils::getArrayValue($general, 'monthly_limit', 0, 1);
			$whereMonth = "created BETWEEN'" . WaicUtils::getConvertedDate(false, 'Y-m-01 00:00:00') . "' AND '" . WaicUtils::getConvertedDate(false, 'Y-m-t 23:59:59') . "'";
			if (!empty($monLimit)) {
				$where = array(
					'task_id' => $taskId,
					'mode' => 0,
					'additionalCondition' => $whereMonth,
				);
				$cntTokens = $hisModel->getCountTokens($where);
				if ($cntTokens >= $monLimit) {
					$isError = true;
					$errMsg = 'Exceeds value: Monthly Limit = ' . $monLimit;
					$task = $workspace->getModel('tasks')->updateTask($taskId, array('status' => 8));
				}
			}
		}
		if (!$isError) {
			if (empty($mode) && WaicUtils::getArrayValue($general, 'e_limit_roles', 0, 1)) {
				$rLimits = WaicUtils::getArrayValue($general, 'limit_roles', array(), 2);
				$uRoles = $isGuest ? array('') : $user->roles;
				$userLimit = '';
				if (!empty($rLimits)) {
					foreach ($rLimits as $limit) {
						$role = WaicUtils::getArrayValue($limit, 'role');
						if (in_array($role, $uRoles)) {
							$userLimit = WaicUtils::getArrayValue($limit, 'max', '', 1, false, true, true);
							 break;
						}
					}
				}
				if ('' !== $userLimit) {
					if (!empty($userLimit)) {
						$where = array(
							'task_id' => $taskId,
							'mode' => 0,
							'additionalCondition' => $whereMonth,
						);
						if ($isGuest) {
							$where['ip'] = $ip;
						} 
						$where['user_id'] = $userId;
						$cntTokens = $hisModel->getCountTokens($where);
					} else {
						$cntTokens = 1;
					}
					if ($cntTokens >= $userLimit) {
						$isError = true;
						$errMsg = 'Exceeds value: Role-Based Limit = ' . $userLimit;
					}
				}
			}
		}
		if (!$isError) {
			if (!empty($message)) {
				$maxInput = WaicUtils::getArrayValue($general, 'max_input', 100, 1);
				$message = WaicUtils::mbsubstr($message, 0, $maxInput);
			}
			
			$maxContext = WaicUtils::getArrayValue($general, 'max_context', 0, 1);
			$needContolLen = !empty($maxContext);
			$prompt = array();
			$apiOptions = WaicUtils::getArrayValue($params, 'api', array(), 2);
			
			$instructions = "You are a chatbot. You strictly follow the given instructions and, while maintaining context, respond with exactly one message to the user's last message, without any additional text or unnecessary information." . PHP_EOL . PHP_EOL;
			
			$apiModel = WaicUtils::getArrayValue($apiOptions, 'model');
			if (strpos($apiModel, 'ft:') === 0) {
				$instructions .= 'You are a fine-tuned AI assistant trained on a proprietary knowledge base. ' . PHP_EOL .
					'You must always attempt to extract answers directly from this internal knowledge base first. ' . PHP_EOL .
					'Only if no relevant information exists in the training data, you may infer an answer — but stay within the logical boundaries of the question. ' . PHP_EOL .
					'Never invent facts that contradict your training. ' . PHP_EOL .
					'If the question is vague, incomplete, or misleading — try to clarify or rephrase it before answering.' . PHP_EOL;
			}
			
			$instructions .= '- Tone of voice: ' . WaicUtils::getArrayValue($apiOptions, 'tone') . PHP_EOL .
				'- Instructions: ' . WaicUtils::getArrayValue($context, 'instructions') . PHP_EOL .
				'Output format (must-follow): ' . PHP_EOL .
				'- Respond only in valid HTML. ' . PHP_EOL . 
				'- Use only content-level HTML tags such as <p>, <ul>, <li>, <strong>, <em> (only if needed). ' . PHP_EOL .
				'- Do not include any document-level tags such as <html>, <head>, or <body>. ' . PHP_EOL .
				'- Return HTML only — no explanations, no extra text.';
				
			$embedId = WaicUtils::getArrayValue($apiOptions, 'embedding', 0, 1);
			if (!empty($embedId)) {
				$instructions .= WaicDispatcher::applyFilters('addEmbeddingText', '', $embedId, $message);
			}
			$aware = '';
			if (!empty($cAware) && WaicUtils::mbstrpos($instructions, '{CONTENT}')) {
				$aware = $cAware;
			}
			if ($needContolLen) {
				$lenInstr = WaicUtils::mbstrlen($instructions);
				$lenContent = $lenInstr;
				$lenAware = WaicUtils::mbstrlen($aware);
				$lenContent += $lenAware;
				$lens = array();
			} else if (!empty($aware)) {
				$instructions = str_replace('{CONTENT}', $aware, $instructions);
			}

			$prompt[] = array('role' => 'system', 'content' => $instructions);
			$maxCntMessages = WaicUtils::getArrayValue($general, 'max_messages', 10, 1);
			$isActive = true;
			if (empty($mode)) {
				$lifetime = WaicUtils::getArrayValue($general, 'lifetime', 0, 1);
				$isActive = $this->isActiveChat($taskId, $userId, $ip, $mode, $lifetime);
			}
			if (isset($options['use_log'])) {
				$isActive = ( true == $options['use_log'] );
			}
			
			$log = $isActive ? $this->getUserChatLog($taskId, $userId, $ip, $mode, $maxCntMessages) : array();
			$log[] = array(
				'question' => $message,
				'answer' => '',
				'file' => $file,
			);
			$n = 1;
			foreach ($log as $l) {
				$question = $l['question'];
				$answer = $l['answer'];
				$fileStr = $l['file'];
				
				if ($needContolLen) {
					$len = WaicUtils::mbstrlen($question);
					if (!empty($fileStr)) {
						$len += WaicUtils::mbstrlen($fileStr);
					}
					$lens[$n] = $len;
					$n++;
					$lenContent += $len;
					if (!empty($answer)) {
						$len = WaicUtils::mbstrlen($answer);
						$lens[$n] = $len;
						$n++;
						$lenContent += $len;
					}
				}
				if (empty($fileStr)) {
					$content = $question;
				} else {
					$content = array();
					if (!empty($question)) {
						$content[] = array('type' => 'text', 'text' => $question);
					}
					$content[] = array(
						'type' => 'image_url', 
						'image_url' => array('url' => $fileStr),
					);
				}
				$prompt[] = array('role' => 'user', 'content' => $content);
				if (!empty($answer)) {
					$prompt[] = array('role' => 'assistant', 'content' => $answer);
				}
			}

			if ($needContolLen) {
				if ($lenContent > $maxContext) {
					$delta = $lenContent - $maxContext;
					if ($delta < $lenAware) {
						$d = $lenAware - $delta;
						$aware = WaicUtils::mbstrlen($aware, 0, $d);
						$lenContent = $maxContext;
					} else {
						$aware = '';
						$lenContent -= $lenAware;
					}
				} 
				
				if ($lenContent > $maxContext) { 
					$delta = $lenContent - $maxContext;
					foreach ($lens as $n => $l) {
						unset($prompt[$n]);
						$lenContent -= $l;
						if ($lenContent <= $maxContext) { 
							break;
						}
					}
					$prompt = array_values($prompt);
				}
				if ($lenContent > $maxContext || count($prompt) < 2) {
					$isError = true;
					$errMsg = 'Exceeds value: Context Max Length = ' . $maxContext;
				} else if (!empty($aware)) {
					$prompt[0]['content'] = str_replace('{CONTENT}', $aware, $prompt[0]['content']);
				}
			}
		}
		$history = array(
			'task_id' => $taskId,
			'user_id' => $userId,
			'ip' => $ip,
			'mode' => $mode,
			'status' => 2,
			'tokens' => 0,
		);
		
		if ($isError) {
			$result = array(
				'his_id' => $hisModel->saveHistory($history),
				'msg' => $errMsg,
				'error' => 1,
			);
		} else {
			$aiProvider = $workspace->getModel('aiprovider')->getInstance($apiOptions);
			if (!$aiProvider) {
				return false;
			}
			$aiProvider->init( $taskId, $userId, $ip, $mode, false );

			if ($aiProvider->setApiOptions($apiOptions)) {
				$opts = array('messages' => $prompt);
				$result = $aiProvider->getText($opts);
			} else {
				$result = array(
					'error' => 1,
					'msg' => WaicFrame::_()->getLastError(),
					'his_id' => $hisModel->saveHistory($history),
				);
			}
		}
		
		$newLog = array(
			'his_id' => $result['his_id'], 
			'question' => $this->controlText($message),
			'answer' => $this->controlText($result['error'] ? $result['msg'] : $result['data']),
			'file' => $file,
			'error' => $result['error'],
			'tt' => WaicUtils::getFormatedDateTime(WaicUtils::getTimestamp(), 'H:i'),
		);

		if (!empty($result['his_id'])) {
			$this->insert($newLog);
		}
		
		if (empty($newLog['error'])) {
			if (!empty($file)) {
				$newLog['question'] = '<img src="' . $file . '">';//__('File uploaded', 'ai-copilot-content-generator');
			}
			if (WaicUtils::getArrayValue($context, 'e_human_request', 0, 1)) {
				$delay = WaicUtils::getArrayValue($context, 'human_request_delay', 0, 1);
				if (!empty($delay)) {
					if ($maxCntMessages < $delay) {
						$where = array(
							'task_id' => $taskId,
							'mode' => $mode,
						);
						if ($isGuest) {
							$where['ip'] = $ip;
						} else {
							$where['user_id'] = $userId;
						}
						$cnt = $hisModel->getCountRequests($where);
					} else {
						$cnt = count($log);
					}
					if ($cnt >= $delay) {
						$newLog['btn'] = array(
							array(
								'link' => '#', 
								'name' => WaicUtils::getArrayValue($context, 'human_request_button'), 
								'class' => 'waic-message-button waic-human-request',
								'uniq' => '.waic-human-request',
							),
						);
					}
				}
			}
		} else {
			$msg = WaicUtils::getArrayValue($context, 'error_message');
			if (!empty($msg)) {
				$newLog['answer'] = $msg;
			}
			if (WaicUtils::getArrayValue($context, 'e_error_request', 0, 1)) {
				$newLog['need_email'] = 1;
				$newLog['request'] = 'error';
				$newLog['plh_email'] = WaicUtils::getArrayValue($context, 'plh_email');
			} else {
				$newLog['disable'] = 1;
			}
		}
		return $newLog;
	}

	public function controlText( $str ) {
		if ( !$str ) {
			return '';
		}
		$str = str_replace(array('```html', '```'), array('', ''), $str);
		return str_replace(array("'"), array('`'), $str);
		//return preg_replace('/\r\n|\r|\n/', '<br>', str_replace(array("'"), array('`'), $str));
	}
	
	public function getHistory( $params ) {
		$length = WaicUtils::getArrayValue($params, 'length', 10, 1);
		$start = WaicUtils::getArrayValue($params, 'start', 0, 1);
		$search = esc_sql(WaicUtils::getArrayValue(WaicUtils::getArrayValue($params, 'search', array(), 2), 'value'));

		$taskId = WaicUtils::getArrayValue($params, 'task_id', 0, 1);
		$where = array();
		$args = array();
		if (!empty($search)) {
			global $wpdb;
			$like = '%' . $wpdb->esc_like($search) . '%';
			if ('admin' == $search) {
				$where[] = 'h.mode=1';
			} else if ('front' == $search) {
				$where[] = 'h.mode=0';
			}
			$where[] = 'h.created LIKE %s';
			$where[] = 'u.user_login LIKE %s';
			$where[] = 'h.ip LIKE %s';
			$where[] = 'EXISTS(SELECT 1 FROM @__chatlogs l WHERE l.his_id=h.id AND (l.question LIKE %s OR l.answer LIKE %s))';
			$args = array($like, $like, $like, $like, $like);
		}
		
		$query = 'SELECT DATE(h.created) as dd, h.user_id, u.user_login, h.ip, h.mode, sum(tokens) as sum_tokens, TIMEDIFF(MAX(h.created),MIN(h.created)) as duration, count(*) as cnt_mes' .
			' FROM @__history as h' .
			' LEFT JOIN #__users u ON (u.id=h.user_id)' .
			' WHERE h.task_id=' . ( (int) $taskId ) .
			( empty($where) ? '' : ' AND (' . implode(' OR ', $where) . ')' ) .
			' GROUP BY DATE(h.created), h.user_id, u.user_login, h.ip, h.mode'; 
		
		$order = WaicUtils::getArrayValue($params, 'order', array(), 2);
		$orderBy = 0;
		$sortOrder = 'desc';
		$orders = array('dd', 'user_login', 'ip', 'mode', 'sum_tokens', 'duration', 'cnt_mes');
		if (isset($order[0])) {
			$orderBy = WaicUtils::getArrayValue($order[0], 'column', $orderBy, 1);
			$sortOrder = WaicUtils::getArrayValue($order[0], 'dir', $sortOrder);
		}
		$query .= ' ORDER BY ' . $orders[$orderBy] . ( 'desc' == strtolower($sortOrder) ? ' desc' : ' asc' );
		$logs = WaicDb::get($query, 'all', ARRAY_A, $args);
		
		$totalCount = empty($logs) ? 0 : count($logs);
		
		if ($length > 0) {
			if ($start >= $totalCount) {
				$start = 0;
			}
			$end = $start + $length;
		} else {
			$end = $totalCount;
		}

		$rows = array();
		if ($totalCount > 0) {
			$view = __('view', 'ai-copilot-content-generator');
			$guest = __('guest', 'ai-copilot-content-generator');
			$modes = array('front', 'admin', 'custom');
			for ($i = $start; $i < $end; $i++) {
				if (!isset($logs[$i])) {
					break;
				}
				$log = $logs[$i];
				$rows[] = array(
					'<div class="waic-log-dd" data-value="' . $log['dd'] . '">' . $log['dd'] . '</div>',
					'<div class="waic-log-user" data-value="' . $log['user_id'] . '">' . ( empty($log['user_id']) ? $guest : $log['user_login'] ) . '</div>',
					'<div class="waic-log-ip" data-value="' . $log['ip'] . '">' . $log['ip'] . '</div>',
					'<div class="waic-log-mode" data-value="' . $log['mode'] . '">' . $modes[$log['mode']] . '</div>',
					'<div class="waic-log-tokens" data-value="' . $log['sum_tokens'] . '">' . $log['sum_tokens'] . '</div>',
					$log['duration'],
					$log['cnt_mes'],
					'<a href="#" class="waic-history-log">' . $view . '</a>',
				);
			}
		}
		return array(
			'data' => $rows,
			'total' => $totalCount,
		);
	}
}
