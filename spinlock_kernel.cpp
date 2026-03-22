#include <pybind11/pybind11.h>
#include <atomic>
#include <chrono>
#include <thread>
#include <iostream>

namespace py = pybind11;

/**
 * Sovereign Spinlock Kernel
 * 
 * Provides bare-metal atomic synchronization for the Sovereign Pulse.
 * Bypasses OS-level mutexes to minimize context-switching jitter.
 */
class SovereignSpinlock {
private:
    std::atomic<uint32_t> lock_flag;
    uint32_t owner_id;

public:
    SovereignSpinlock() : lock_flag(0), owner_id(0) {}

    bool try_acquire(uint32_t id) {
        uint32_t expected = 0;
        if (lock_flag.compare_exchange_strong(expected, 1, std::memory_order_acquire)) {
            owner_id = id;
            return true;
        }
        return false;
    }

    void acquire(uint32_t id) {
        uint32_t expected = 0;
        // Standard spin-loop with yield to stay friendly to the OS while maintaining low latency
        while (!lock_flag.compare_exchange_weak(expected, 1, std::memory_order_acquire)) {
            expected = 0;
            std::this_thread::yield(); 
        }
        owner_id = id;
    }

    void release() {
        owner_id = 0;
        lock_flag.store(0, std::memory_order_release);
    }

    bool is_locked() const {
        return lock_flag.load(std::memory_order_relaxed) == 1;
    }

    uint32_t get_owner() const {
        return owner_id;
    }
};

PYBIND11_MODULE(sovereign_spinlock, m) {
    m.doc() = "Genlex Hardware Spinlock Kernel for Pulse Sovereignty";

    py::class_<SovereignSpinlock>(m, "SovereignSpinlock")
        .def(py::init<>())
        .def("try_acquire", &SovereignSpinlock::try_acquire, "Attempt to acquire the lock immediately.")
        .def("acquire", &SovereignSpinlock::acquire, "Spin until the lock is acquired.")
        .def("release", &SovereignSpinlock::release, "Release the sovereign lock.")
        .def("is_locked", &SovereignSpinlock::is_locked, "Check if the lock is currently held.")
        .def("get_owner", &SovereignSpinlock::get_owner, "Get the current owner ID.");
}
