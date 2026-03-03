// Todo List Application JavaScript

(function () {
  'use strict';

  // ─── State ───
  const state = {
    todos: {},           // keyed by id for quick lookup
    currentCategory: null, // null = "All"
    inFlight: {},        // track in-flight requests per todo id
  };

  // ─── DOM References ───
  const todoList = document.getElementById('todo-list');
  const stateLoading = document.getElementById('state-loading');
  const stateEmpty = document.getElementById('state-empty');
  const stateError = document.getElementById('state-error');
  const retryBtn = document.getElementById('retry-btn');
  const todoForm = document.getElementById('todo-form');
  const titleInput = document.getElementById('title-input');
  const titleError = document.getElementById('title-error');
  const descInput = document.getElementById('desc-input');
  const catSelect = document.getElementById('cat-select');
  const submitBtn = document.getElementById('submit-btn');
  const ariaLive = document.getElementById('aria-live');
  const toast = document.getElementById('toast');

  // ─── API Helpers ───

  async function apiFetch(url, options = {}) {
    const resp = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    return resp;
  }

  // ─── Announce for screen readers ───

  function announce(message) {
    if (ariaLive) {
      ariaLive.textContent = message;
    }
  }

  // ─── Toast ───

  function showToast(message, type = 'error') {
    toast.textContent = message;
    toast.className = 'toast toast--' + type;
    setTimeout(function () {
      toast.classList.add('toast--hidden');
    }, 4000);
  }

  // ─── Render ───

  function showState(name) {
    todoList.hidden = name !== 'list';
    stateLoading.hidden = name !== 'loading';
    stateEmpty.hidden = name !== 'empty';
    stateError.hidden = name !== 'error';
  }

  function renderTodos(todos) {
    todoList.innerHTML = '';

    if (todos.length === 0) {
      if (state.currentCategory) {
        stateEmpty.textContent = 'No ' + state.currentCategory + ' todos yet.';
      } else {
        stateEmpty.textContent = 'No todos yet. Add one above to get started.';
      }
      showState('empty');
      return;
    }

    showState('list');

    todos.forEach(function (todo) {
      state.todos[todo.id] = todo;
      var li = createTodoElement(todo);
      todoList.appendChild(li);
    });
  }

  function createTodoElement(todo) {
    var li = document.createElement('li');
    li.className = 'todo-item' + (todo.is_completed ? ' todo-item--completed' : '');
    li.dataset.id = todo.id;

    // Checkbox
    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'todo-item__checkbox';
    checkbox.checked = todo.is_completed;
    checkbox.setAttribute(
      'aria-label',
      (todo.is_completed ? 'Mark "' : 'Mark "') + todo.title + (todo.is_completed ? '" as incomplete' : '" as complete')
    );
    checkbox.addEventListener('change', function () {
      handleToggle(todo.id, checkbox);
    });

    // Title
    var titleSpan = document.createElement('span');
    titleSpan.className = 'todo-item__title';
    titleSpan.textContent = todo.title;

    // Badge
    var badge = document.createElement('span');
    badge.className = 'badge badge--' + todo.category;
    badge.textContent = todo.category.charAt(0).toUpperCase() + todo.category.slice(1);

    // Delete button
    var actions = document.createElement('div');
    actions.className = 'todo-item__actions';
    var deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn-destructive';
    deleteBtn.setAttribute('aria-label', 'Delete "' + todo.title + '"');
    deleteBtn.innerHTML = '<svg class="delete-icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>';
    deleteBtn.addEventListener('click', function () {
      handleDelete(todo.id, li);
    });
    actions.appendChild(deleteBtn);

    li.appendChild(checkbox);
    li.appendChild(titleSpan);
    li.appendChild(badge);
    li.appendChild(actions);

    return li;
  }

  // ─── Fetch Todos ───

  async function fetchTodos(category) {
    showState('loading');
    announce('Loading todos...');

    try {
      var url = '/api/todos';
      if (category) {
        url += '?category=' + encodeURIComponent(category);
      }
      var resp = await apiFetch(url);
      if (!resp.ok) {
        throw new Error('Failed to fetch');
      }
      var todos = await resp.json();
      renderTodos(todos);
    } catch (e) {
      showState('error');
    }
  }

  // ─── Toggle Completion ───

  async function handleToggle(todoId, checkbox) {
    if (state.inFlight[todoId]) {
      // Revert checkbox -- request already in flight
      checkbox.checked = !checkbox.checked;
      return;
    }

    var todo = state.todos[todoId];
    if (!todo) return;

    var li = todoList.querySelector('[data-id="' + todoId + '"]');
    var newCompleted = !todo.is_completed;

    // Optimistic UI
    state.inFlight[todoId] = true;
    li.classList.toggle('todo-item--completed', newCompleted);
    checkbox.checked = newCompleted;

    try {
      var resp = await apiFetch('/api/todos/' + todoId, {
        method: 'PUT',
        body: JSON.stringify({
          title: todo.title,
          description: todo.description,
          category: todo.category,
          is_completed: newCompleted,
        }),
      });

      if (!resp.ok) {
        throw new Error('Failed to update');
      }

      // Update local state
      var updated = await resp.json();
      state.todos[todoId] = updated;
      announce(newCompleted ? 'Todo marked as complete.' : 'Todo marked as incomplete.');
    } catch (e) {
      // Revert optimistic UI
      li.classList.toggle('todo-item--completed', todo.is_completed);
      checkbox.checked = todo.is_completed;
      showToast('Could not update todo. Please try again.', 'error');
    } finally {
      delete state.inFlight[todoId];
    }
  }

  // ─── Delete Todo ───

  async function handleDelete(todoId, li) {
    if (!confirm('Are you sure you want to delete this todo?')) {
      return;
    }

    var todo = state.todos[todoId];

    // Optimistic removal
    li.remove();
    delete state.todos[todoId];

    // Check if list is now empty
    if (todoList.children.length === 0) {
      if (state.currentCategory) {
        stateEmpty.textContent = 'No ' + state.currentCategory + ' todos yet.';
      } else {
        stateEmpty.textContent = 'No todos yet. Add one above to get started.';
      }
      showState('empty');
    }

    try {
      var resp = await apiFetch('/api/todos/' + todoId, { method: 'DELETE' });
      if (!resp.ok && resp.status !== 204) {
        throw new Error('Failed to delete');
      }
      announce('Todo deleted.');
    } catch (e) {
      // Re-insert on failure
      state.todos[todoId] = todo;
      var newLi = createTodoElement(todo);
      todoList.appendChild(newLi);
      showState('list');
      showToast('Could not delete todo. Please try again.', 'error');
    }
  }

  // ─── Form Submit ───

  todoForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Clear previous errors
    titleInput.classList.remove('input-text--error');
    titleError.hidden = true;

    var title = titleInput.value.trim();
    if (title.length === 0) {
      titleInput.classList.add('input-text--error');
      titleError.hidden = false;
      titleInput.focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Adding...';

    try {
      var body = {
        title: title,
        description: descInput.value.trim() || null,
        category: catSelect.value,
      };

      var resp = await apiFetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify(body),
      });

      if (!resp.ok) {
        throw new Error('Failed to create');
      }

      // Clear form
      titleInput.value = '';
      descInput.value = '';
      titleInput.focus();

      announce('Todo added successfully.');

      // Re-fetch with current filter
      await fetchTodos(state.currentCategory);
    } catch (e) {
      showToast('Could not add todo. Please try again.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Add';
    }
  });

  // ─── Category Tabs ───

  var tabs = document.querySelectorAll('.tab');
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) {
        t.setAttribute('aria-selected', 'false');
      });
      tab.setAttribute('aria-selected', 'true');

      var category = tab.dataset.category;
      state.currentCategory = category === 'all' ? null : category;
      fetchTodos(state.currentCategory);
    });

    // Keyboard navigation for tabs
    tab.addEventListener('keydown', function (e) {
      var tabArr = Array.from(tabs);
      var index = tabArr.indexOf(tab);
      if (e.key === 'ArrowRight' && index < tabArr.length - 1) {
        tabArr[index + 1].focus();
        tabArr[index + 1].click();
        e.preventDefault();
      }
      if (e.key === 'ArrowLeft' && index > 0) {
        tabArr[index - 1].focus();
        tabArr[index - 1].click();
        e.preventDefault();
      }
    });
  });

  // ─── Retry Button ───

  if (retryBtn) {
    retryBtn.addEventListener('click', function () {
      fetchTodos(state.currentCategory);
    });
  }

  // ─── Init ───

  fetchTodos(null);

})();
