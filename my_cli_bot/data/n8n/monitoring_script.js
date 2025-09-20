
      // N8N Monitoring Script
      const checkWorkflowStatus = async () => {
        try {
          const response = await fetch('http://localhost:5678/api/v1/workflows/purdue-cs-curriculum');
          const workflow = await response.json();
          
          return {
            active: workflow.active,
            lastRun: workflow.updatedAt,
            status: workflow.active ? 'running' : 'stopped'
          };
        } catch (error) {
          console.error('Monitoring error:', error);
          return { status: 'error', error: error.message };
        }
      };
      
      // Run monitoring every 5 minutes
      setInterval(checkWorkflowStatus, 300000);
    